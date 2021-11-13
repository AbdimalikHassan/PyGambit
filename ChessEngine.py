# This class is responsible for storing all the information about the state of the chess game.
# It will also be responsible for determining the valid moves at the current state.
# It will also keep a move log

class GameState():
    def __init__(self):
        # board is an 8x8 2d list, each element of the list has 2 characters.
        # The first character represents the color of the piece, 'b' or 'w'
        # "--" represents an empty space with no piece.
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR" ],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        ]
        self.moveFunctions = {"p":self.getPawnMoves, "R":self.getRookMoves, "K":self.getKingMoves, 
                              "Q":self.getQueenMoves, "N":self.getKnightMoves, "B":self.getBishopMoves}
        self.whiteToMove = True
        self.moveLog = []
        self.inCheck = False
        self.pins = []
        self.checks = []
        self.blackKingLocation = (0, 4)
        self.whiteKingLocation = (7, 4)

    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move) # add move to move bank for undo
        self.whiteToMove = not self.whiteToMove # toggle white turn
        # update king location if moved
        if move.pieceMoved == "bK":
            self.blackKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == "wK":
            self.whiteKingLocation = (move.endRow, move.endCol)
        # Pawn promotion
        if move.isPawnPromotion:
            promotionPiece = input("Promote to Q, R, B, or N: ") # add to ui later
            self.board[move.endRow][move.endCol] = self.pieceMoved[0] + promotionPiece
        # Enpassant move
        if move.isEnpassantMove:
            self.board[move.startRow][move.endCol] = "--"
        
        # Update enpassantPossible variable
        if move.pieceMoved[1] == "p" and abs(move.startRow - move.endRow) == 2: # clever way of checking 2 square pawn advance irrespective of color
            self.enpassantPossible = ((move.startRow + move.endRow) // 2, move.startCol)
        else:
            self.enpassantPossible = ()

    def undoMove(self):
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove
            # update king location if moved
            if move.pieceMoved == "bK":
                self.blackKingLocation = (move.endRow, move.endCol)
            elif move.pieceMoved == "wK":
                self.whiteKingLocation = (move.endRow, move.endCol)
            if move.isEnpassantMove:
                self.board[move.endRow][move.endCol] = "--" # leave landing square blank
                self.board[move.startRow][move.endCol] = move.pieceCaptured
                self.enpassantPossible = (move.endRow, move.endCol)
            # Undoing a 2 square pawn advance should reset enpassantPossible
            if move.pieceMoved[1] == "p" and abs(move.startRow - move.endRow) == 2:
                self.enpassantPossible = ()
    
    # All moves, considers checks
    def getValidMoves(self):
        moves = []
        self.inCheck, self.pins, self.checks = self.checkForPinsAndChecks()
        if self.whiteToMove:
            kingRow = self.whiteKingLocation[0]
            kingCol = self.whiteKingLocation[1]
        else:
            kingRow = self.blackKingLocation[0]
            kingCol = self.blackKingLocation[1]
        
        if self.inCheck:
            if len(self.checks) == 1: # only 1 piece delivering check.
                # you must block check (exception being the knight), capture the piece, or move to safety
                moves = self.getAllPossibleMoves()
                check = self.checks[0]
                checkRow = check[0]
                checkCol = check[1]
                pieceChecking = self.board[checkRow][checkCol]
                validSquares = []
                
                # Knights cannot be blocked
                if pieceChecking[1] == "N":
                    validSquares = [(checkRow, checkCol)]
                else:
                    for i in range(1,8):
                        validSquare = (kingRow + check[2]*i, kingCol + check[3]*i) # check[2] and check[3] are the directions
                        validSquares.append(validSquare)
                        if validSquare[0] == checkRow and validSquare[1] == checkCol: # we've arrived at piece delivering check
                            break
                
                # Filter out any moves that don't block, capture, or move King to safety
                for i in range(len(moves)- 1, -1, -1): # when removing from a list, moving backwards avoids indexing issues
                    if moves[i].pieceMoved[1] != "K": # Doesn't move king so move must block or capture
                        if not (moves[i].endRow, moves[i].endCol) in validSquares:
                            moves.remove(moves[i])

            else: # double check (there is no triple check or beyond)
                # only option is to move to safety
                self.getKingMoves(kingRow, kingCol, moves)
        else: # you're not in check so you can move in any way you want barring pinned pieces.
            moves = self.getAllPossibleMoves()
        return moves

    # All moves, not considering checks
    def getAllPossibleMoves(self):
        moves = []
        for row in range(len(self.board)):
            for col in range(len(self.board[row])):
                turn = self.board[row][col][0] # color of the piece, "w" or "b"
                if (turn == "w" and self.whiteToMove) or (turn == "b" and not self.whiteToMove):
                    piece = self.board[row][col][1]
                    self.moveFunctions[piece](row, col, moves) # python doesn't have a switch statement

        return moves

    def getPawnMoves(self, row, col, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piecePinned = True
                print(str(row) + str(col))
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
            
        if self.whiteToMove:
            moveAmount = -1
            startRow = 6
            backRow = 0
            enemyColor = "b"
        else:
            moveAmount = 1
            startRow = 1
            backRow = 7
            enemyColor = "w"
        isPawnPromotion = False

        # Pawn pushes
        if self.board[row+moveAmount][col] == "--": # 1 tile pawn push
            if not piecePinned or pinDirection == (-1, 0):
                if row + moveAmount == backRow:
                    isPawnPromotion = True
                moves.append(Move((row, col), (row+moveAmount, col), self.board, isPawnPromotion=isPawnPromotion))
                # Check 2 spaces ahead only after checking one space ahead!
                if row == startRow and self.board[row + (2*moveAmount)][col] == "--": # 2 tile pawn push can only occur on 2nd rank for white pawns
                    moves.append(Move((row, col),((row + (2*moveAmount)), col), self.board))
        # Pawn captures
        if col - 1 >= 0: # captures to the left (left being col 0)
            if self.board[row+moveAmount][col-1][0] == enemyColor: # enemy piece to capture
                if not piecePinned or pinDirection == (-1, -1):
                    if row + moveAmount == backRow:
                        isPawnPromotion = True
                    moves.append(Move((row, col), (row+moveAmount, col-1), self.board, isPawnPromotion=isPawnPromotion))
        if col + 1 < 8: # captures to the right (right being col 7)
            if self.board[row+moveAmount][col+1][0] == enemyColor: # enemy piece to capture
                if not piecePinned or pinDirection == (-1, 1):
                    if row + moveAmount == backRow:
                        isPawnPromotion = True
                    moves.append(Move((row, col), (row+moveAmount, col+1), self.board, isPawnPromotion=isPawnPromotion))                 
        

    def getRookMoves(self, row, col, moves):
        directions = ((-1,0), (1,0), (0,-1), (0,1))
        enemyColor = "b" if self.whiteToMove else "w"
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                if self.board[row][col][1] != "Q": #can't remove queen from pin on rook moves before you've evaluated bishop moves
                    self.pins.remove(self.pins[i])
                    break

        for direction in directions:
            for i in range(1,8): # only need to check a max of 7 tiles in a given direction
                endRow = row + direction[0] * i
                endCol = col + direction[1] * i
                if(0 < endRow < 8 and 0 < endCol < 8): # check if spot is on the board
                    if not piecePinned or pinDirection == direction or pinDirection == (-direction[0], -direction[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == "--":
                            moves.append(Move((row, col), (endRow, endCol), self.board))
                        elif endPiece[0] == enemyColor:
                            moves.append(Move((row, col), (endRow, endCol), self.board))
                            break # quit searching in this direction, can't jump over pieces
                        else:
                            break
                    else: # off board
                        break

    def getKingMoves(self, row, col, moves):
        rowMoves = (-1, -1, -1, 0, 0, 1, 1, 1)
        colMoves = (-1, 0, 1, -1, 1, -1, 0, 1)
        allyColor = "w" if self.whiteToMove else "b"

        for i in range(8):
            endRow = row + rowMoves[i]
            endCol = col + colMoves[i]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:# if the spot you're considering isn't already occupied by an ally
                    if allyColor == "w": # hypothetically "make" each of the 8 possible king moves
                        self.whiteKingLocation = (endRow, endCol)
                    else:
                        self.blackKingLocation = (endRow, endCol)
                    
                    inCheck, pins, checks = self.checkForPinsAndChecks() # check if "making" that move put you in check
                    if not inCheck: # if "making" that move ended up being safe, it's valid!
                        moves.append(Move((row, col), (endRow, endCol), self.board))
                    
                    if allyColor == "w": # clean up your hypothetical king move (reset king)
                        self.whiteKingLocation = (row, col)
                    else:
                        self.blackKingLocation = (row, col)
    
    def getQueenMoves(self, row, col, moves):
        self.getRookMoves(row, col, moves)
        self.getBishopMoves(row, col, moves)

    def getKnightMoves(self, row, col, moves):
        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        allyColor = "w" if self.whiteToMove else "b"
        piecePinned = False
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piecePinned = True
                self.pins.remove(self.pins[i])
                break

        for knightMove in knightMoves:
            endRow = row + knightMove[0]
            endCol = col + knightMove[1]
            if(0 <= endRow < 8 and 0 <= endCol < 8):
                if not piecePinned:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] != allyColor:
                        moves.append(Move((row, col), (endRow, endCol), self.board))

    def getBishopMoves(self, row, col, moves):
        directions = ((-1,-1), (-1,1), (1,-1), (1,1))
        enemyColor = "b" if self.whiteToMove else "w"
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        for direction in directions:
            for i in range(1,8): # only need to check a max of 7 tiles in a given direction
                endRow = row + direction[0] * i
                endCol = col + direction[1] * i
                if(0 <= endRow < 8 and 0 <= endCol < 8): # check if spot is on the board
                    if not piecePinned or pinDirection == direction or pinDirection == (-direction[0], -direction[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == "--":
                            moves.append(Move((row, col), (endRow, endCol), self.board))
                        elif endPiece[0] == enemyColor:
                            moves.append(Move((row, col), (endRow, endCol), self.board))
                            break # quit searching in this direction, can't jump over pieces
                        else:
                            break
                    else: # off board
                        break
    
    def checkForPinsAndChecks(self):
        inCheck = False
        pins = [] # holds squares where allied pinned pieces are and directions they're pinned from
        checks = [] # squares where enemy piece is applying a check
        
        if self.whiteToMove:
            enemyColor = "b"
            allyColor = "w"
            startRow = self.whiteKingLocation[0]
            startCol = self.whiteKingLocation[1]
        else:
            enemyColor = "w"
            allyColor = "b"
            startRow = self.blackKingLocation[0]
            startCol = self.blackKingLocation[1]
        
        # move outward from king to find pins and checks
        directions = ((0, -1), (-1, 0), (0, 1), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1))
        for i in range(len(directions)):
            d = directions[i]
            possiblePin = () # reset possible pin
            for j in range(1,8):
                endRow = startRow + d[0]*j
                endCol = startCol + d[1]*j
                if 0 <= endRow < 8 and 0 <= endCol < 8: # spot is on the board
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] == allyColor and endPiece[1] != "K": # king moves function creates phantom king
                        if possiblePin == (): # 1st allied piece in a given direction could be pinned
                            possiblePin = (endRow, endCol, d[0], d[1])
                        else:
                            break
                    elif endPiece[0] == enemyColor:
                        type = endPiece[1] # are we dealing with a rook, bishop, etc?
                        # 5 possibilities here that we care about
                        # 1) Orthogonally away from king (N,E,S,W) and piece is a Rook
                        # 2) Diagonally away from king and piece is a Bishop
                        # 3) 1 square away diagonally from King and piece is a pawn (travelling toward King)
                        # 4) Any direction and piece is a Queen
                        # 5) Any direction, 1 square away, and piece is another King
                        if ((0 <= i <= 3 and type == "R") or
                            (4 <= i <= 7 and type == "B") or
                            (j == 1 and type == "p" and ((enemyColor == "w" and 6 <= i <= 7) or (enemyColor == "b" and 4 <= i <= 5))) or
                            (type == "Q") or
                            (j == 1 and type == "K")):
                            if possiblePin == ():
                                inCheck = True
                                checks.append((endRow, endCol, d[0], d[1]))
                                break
                            else:
                                pins.append(possiblePin)
                                break
                        else: # We have an enemy piece that isn't applying or preparing to apply check
                            break
                else:
                    break # spot is not on the board

        # Don't forget to check for knight checks    
        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        for knightMove in knightMoves:
            endRow = startRow + knightMove[0]
            endCol = startCol + knightMove[1]
            if(0 <= endRow < 8 and 0 <= endCol < 8):
                endPiece = self.board[endRow][endCol] 
                if endPiece[0] == enemyColor and endPiece[1] == "N":
                    inCheck = True
                    checks.append((endRow, endCol, knightMove[0], knightMove[1]))
        
        return inCheck, pins, checks

class Move():
    ranksToRows = {"1":7, "2":6, "3":5, "4":4, "5":3, "6":2, "7":1, "8":0}
    rowsToRanks = {v:k for k,v in ranksToRows.items()}

    filesToCols = {"a":0, "b":1, "c":2, "d":3,"e":4, "f":5, "g":6, "h":7}
    colsToFiles = {v:k for k,v in filesToCols.items()}

    def __init__(self, startSq, endSq, board, isEnpassantMove=False, isPawnPromotion=False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.isPawnPromotion = isPawnPromotion
        self.isEnpassantMove = isEnpassantMove
        if isEnpassantMove:
            self.pieceCaptured = "bp" if self.pieceMoved == "wp" else "wp"
        self.moveID = 1000*self.startRow + 100*self.startCol + 10*self.endRow + self.endCol
    
    # Overriding the equals method
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def getChessNotation(self):
        # Does not account for pawns only having destination noted
        # Does not account for captured piece notation
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self, row, col):
        return self.colsToFiles[col] + self.rowsToRanks[row]