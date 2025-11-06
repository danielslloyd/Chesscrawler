"""
Chess movement logic for the dungeon crawler.
Each piece type has unique movement patterns.
"""

class ChessMove:
    """Base class for chess piece movement patterns."""

    @staticmethod
    def get_pawn_moves(x, y, board_size, is_first_move=False):
        """Pawn moves forward, attacks diagonally."""
        moves = []
        # Forward movement
        if y > 0:
            moves.append((x, y - 1))
            if is_first_move and y > 1:
                moves.append((x, y - 2))
        # Diagonal attacks
        attack_moves = []
        if y > 0:
            if x > 0:
                attack_moves.append((x - 1, y - 1))
            if x < board_size - 1:
                attack_moves.append((x + 1, y - 1))
        return moves, attack_moves

    @staticmethod
    def get_rook_moves(x, y, board_size, max_range=None):
        """Rook moves in straight lines (horizontal/vertical)."""
        moves = []
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]

        for dx, dy in directions:
            steps = 1
            while True:
                if max_range and steps > max_range:
                    break
                nx, ny = x + dx * steps, y + dy * steps
                if 0 <= nx < board_size and 0 <= ny < board_size:
                    moves.append((nx, ny))
                    steps += 1
                else:
                    break
        return moves

    @staticmethod
    def get_bishop_moves(x, y, board_size, max_range=None):
        """Bishop moves diagonally."""
        moves = []
        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]

        for dx, dy in directions:
            steps = 1
            while True:
                if max_range and steps > max_range:
                    break
                nx, ny = x + dx * steps, y + dy * steps
                if 0 <= nx < board_size and 0 <= ny < board_size:
                    moves.append((nx, ny))
                    steps += 1
                else:
                    break
        return moves

    @staticmethod
    def get_knight_moves(x, y, board_size):
        """Knight moves in L-shape (2+1 squares)."""
        moves = []
        knight_offsets = [
            (2, 1), (2, -1), (-2, 1), (-2, -1),
            (1, 2), (1, -2), (-1, 2), (-1, -2)
        ]

        for dx, dy in knight_offsets:
            nx, ny = x + dx, y + dy
            if 0 <= nx < board_size and 0 <= ny < board_size:
                moves.append((nx, ny))
        return moves

    @staticmethod
    def get_queen_moves(x, y, board_size, max_range=None):
        """Queen moves like rook + bishop combined."""
        moves = ChessMove.get_rook_moves(x, y, board_size, max_range)
        moves.extend(ChessMove.get_bishop_moves(x, y, board_size, max_range))
        return moves

    @staticmethod
    def get_king_moves(x, y, board_size):
        """King moves one square in any direction."""
        moves = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < board_size and 0 <= ny < board_size:
                    moves.append((nx, ny))
        return moves

    @staticmethod
    def filter_moves_by_obstacles(moves, obstacles, current_piece_type=None):
        """
        Filter moves based on obstacles (walls, doors, etc.).
        Knights can jump over obstacles, others cannot.
        """
        if current_piece_type == 'knight':
            # Knights can jump, so only check destination
            return [move for move in moves if move not in obstacles]

        # For other pieces, we need to check the path
        # This is simplified - in full implementation, would trace the path
        return [move for move in moves if move not in obstacles]

    @staticmethod
    def get_moves_for_piece(piece_type, x, y, board_size, obstacles=None, **kwargs):
        """
        Get all valid moves for a piece type at position (x, y).

        Args:
            piece_type: 'pawn', 'rook', 'bishop', 'knight', 'queen', 'king'
            x, y: Current position
            board_size: Size of the board
            obstacles: Set of (x, y) positions that block movement
            **kwargs: Additional piece-specific parameters

        Returns:
            List of valid (x, y) positions, or tuple of (moves, attacks) for pawn
        """
        if obstacles is None:
            obstacles = set()

        if piece_type == 'pawn':
            moves, attacks = ChessMove.get_pawn_moves(
                x, y, board_size, kwargs.get('is_first_move', False)
            )
            moves = ChessMove.filter_moves_by_obstacles(moves, obstacles, 'pawn')
            attacks = ChessMove.filter_moves_by_obstacles(attacks, obstacles, 'pawn')
            return moves, attacks
        elif piece_type == 'rook':
            moves = ChessMove.get_rook_moves(x, y, board_size, kwargs.get('max_range'))
        elif piece_type == 'bishop':
            moves = ChessMove.get_bishop_moves(x, y, board_size, kwargs.get('max_range'))
        elif piece_type == 'knight':
            moves = ChessMove.get_knight_moves(x, y, board_size)
        elif piece_type == 'queen':
            moves = ChessMove.get_queen_moves(x, y, board_size, kwargs.get('max_range'))
        elif piece_type == 'king':
            moves = ChessMove.get_king_moves(x, y, board_size)
        else:
            return []

        return ChessMove.filter_moves_by_obstacles(moves, obstacles, piece_type)
