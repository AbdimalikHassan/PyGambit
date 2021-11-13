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
        self.blackKingLocation = (0, 4)
        self.whiteKingLocation = (7, 4)
        self.checkMate = False
        self.staleMate = False


    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move) # add move to move bank for undo
        self.whiteToMove = not self.whiteToMove # toggle white turn
        if move.pieceMoved == "bK":
            self.blackKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == "wK":
            self.whiteKingLocation = (move.endRow, move.endCol)

    def undoMove(self):
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove
            if move.pieceMoved == "bK":
                self.blackKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == "wK":
                self.whiteKingLocation = (move.startRow, move.startCol)
    
    # All moves, considers checks
    def getValidMoves(self):
        # 5 step algorithm:
        # 1) Generate all possible moves
        moves = self.getAllPossibleMoves()
        # 2) For each move, make the move
        for i in range(len(moves)-1, -1, -1):
            self.makeMove(moves[i])
            # 3) Generate all opponent's moves
            # 4) For each of your opponents moves, see if they attack the king
            self.whiteToMove = not self.whiteToMove # make sure inCheck() is running from the correct perspective 
            if self.inCheck():
                moves.remove(moves[i]) # 5) if they do attack your king, not a valid move
            self.whiteToMove = not self.whiteToMove
            self.undoMove()
        if len(moves) == 0: # either checkmate or stalemate
            if self.inCheck():
                self.checkMate = True
            else:
                self.staleMate = True
        else: # undo a move where stalemate or checkmate was true
            self.checkMate = False
            self.staleMate = False
        return moves

    def inCheck(self):
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:
            return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])

    # Determine if the enemy can attack square row, col (used with king location)
    def squareUnderAttack(self, row, col):
        self.whiteToMove = not self.whiteToMove # switch to opponents POV
        oppMoves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove # switch back from opponents POV
        for move in oppMoves:
            if move.endRow == row and move.endCol == col:
                return True
        return False
    
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
        if self.whiteToMove: # white pawn moves
            # Pawn pushes
            if self.board[row-1][col] == "--": # 1 tile pawn push
                moves.append(Move((row, col), (row-1, col), self.board))
                # Check 2 spaces ahead only after checking one space ahead!
                if self.board[row-2][col] == "--" and row == 6: # 2 tile pawn push can only occur on 2nd rank for white pawns
                    moves.append(Move((row, col),(row -2, col), self.board))
            # Pawn captures
            if col - 1 >= 0: # captures to the left (left being col 0)
                if self.board[row-1][col-1][0] == "b": # enemy piece to capture
                    moves.append(Move((row, col), (row-1, col-1), self.board))
            if col + 1 < 8: # captures to the right (right being col 7)
                if self.board[row-1][col+1][0] == "b": # enemy piece to capture
                    moves.append(Move((row, col), (row-1, col+1), self.board))                    
        else: # black pawn moves
            # Pawn pushes
            if self.board[row+1][col] == "--": # 1 tile pawn push
                moves.append(Move((row, col), (row+1, col), self.board))
            # Check 2 spaces ahead only after checking one space ahead!
                if self.board[row+2][col] == "--" and row == 1: # 2 tile pawn push can only occur on 7th rank for black pawns
                    moves.append(Move((row, col),(row+2, col), self.board))
            # Pawn captures
            if col - 1 >= 0: # captures to the left (left being col 0)
                if self.board[row+1][col-1][0] == "w": # enemy piece to capture
                    moves.append(Move((row, col), (row+1, col-1), self.board))
            if col + 1 < 8: # captures to the right (right being col 7)
                if self.board[row+1][col+1][0] == "w": # enemy piece to capture 
                    moves.append(Move((row, col), (row+1, col+1), self.board))
                    # Add pawn promotions later

    def getRookMoves(self, row, col, moves):
        directions = ((-1,0), (1,0), (0,-1), (0,1))
        enemyColor = "b" if self.whiteToMove else "w"
        for direction in directions:
            for i in range(1,8): # only need to check a max of 7 tiles in a given direction
                endRow = row + direction[0] * i
                endCol = col + direction[1] * i
                if(0 < endRow < 8 and 0 < endCol < 8): # check if spot is on the board
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
        kingMoves = ((-1,-1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))
        allyColor = "w" if self.whiteToMove else "b"
        for i in range(8):
            endRow = row + kingMoves[i][0]
            endCol = col + kingMoves[i][1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:# if the spot you're considering isn't already occupied by an ally
                    moves.append(Move((row, col), (endRow, endCol), self.board))
    
    def getQueenMoves(self, row, col, moves):
        self.getRookMoves(row, col, moves)
        self.getBishopMoves(row, col, moves)

    def getKnightMoves(self, row, col, moves):
        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        allyColor = "w" if self.whiteToMove else "b"
        for knightMove in knightMoves:
            endRow = row + knightMove[0]
            endCol = col + knightMove[1]
            if(0 <= endRow < 8 and 0 <= endCol < 8):
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:
                    moves.append(Move((row, col), (endRow, endCol), self.board))

    def getBishopMoves(self, row, col, moves):
        directions = ((-1,-1), (-1,1), (1,-1), (1,1))
        enemyColor = "b" if self.whiteToMove else "w"
        for direction in directions:
            for i in range(1,8): # only need to check a max of 7 tiles in a given direction
                endRow = row + direction[0] * i
                endCol = col + direction[1] * i
                if(0 <= endRow < 8 and 0 <= endCol < 8): # check if spot is on the board
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

class Move():
    ranksToRows = {"1":7, "2":6, "3":5, "4":4, "5":3, "6":2, "7":1, "8":0}
    rowsToRanks = {v:k for k,v in ranksToRows.items()}

    filesToCols = {"a":0, "b":1, "c":2, "d":3,"e":4, "f":5, "g":6, "h":7}
    colsToFiles = {v:k for k,v in filesToCols.items()}

    def __init__(self, startSq, endSq, board):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
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