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
            ["--", "--", "--", "--", "bp", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        ]
        self.moveFunctions = {"p":self.getPawnMoves, "R":self.getRookMoves, "K":self.getKingMoves, 
                              "Q":self.getQueenMoves, "N":self.getKnightMoves, "B":self.getBishopMoves}
        self.whiteToMove = True
        self.moveLog = []

    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move) # add move to move bank for undo
        self.whiteToMove = not self.whiteToMove # toggle white turn

    def undoMove(self):
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove
    
    # All moves, considers checks
    def getValidMoves(self):
        return self.getAllPossibleMoves()

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

    def getRookMoves(self, row, col, moves):
        pass

    def getKingMoves(self, row, col, moves):
        pass
    
    def getQueenMoves(self, row, col, moves):
        pass

    def getKnightMoves(self, row, col, moves):
        pass

    def getBishopMoves(self, row, col, moves):
        pass

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