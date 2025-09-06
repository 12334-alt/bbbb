import requests
import chess.pgn
import io

USERNAME = "ToromBot"
OUTPUT_FILE = "torombot_draws_3000.pgn"

def stream_and_filter(username, output_file):
    url = f"https://lichess.org/api/games/user/{username}"
    headers = {"Accept": "application/x-chess-pgn"}
    params = {
        "rated": "true",
        "moves": "true",
    }

    with requests.get(url, headers=headers, params=params, stream=True) as response:
        response.raise_for_status()

        infile = io.StringIO()
        with open(output_file, "w", encoding="utf-8") as outfile:
            for chunk in response.iter_content(chunk_size=4096, decode_unicode=True):
                if not chunk:
                    continue
                infile.write(chunk)

                infile.seek(0)
                while True:
                    try:
                        game = chess.pgn.read_game(infile)
                    except Exception:
                        break

                    if game is None:
                        break

                    rest = infile.read()
                    infile = io.StringIO(rest)

                    if game.headers.get("Result") != "1/2-1/2":
                        continue

                    if game.headers.get("White") != USERNAME and game.headers.get("Black") != USERNAME:
                        continue

                    white_elo = int(game.headers.get("WhiteElo", "0"))
                    black_elo = int(game.headers.get("BlackElo", "0"))
                    if white_elo < 3000 or black_elo < 3000:
                        continue

                    print(game, file=outfile, end="\n\n")

if __name__ == "__main__":
    stream_and_filter(USERNAME, OUTPUT_FILE)
