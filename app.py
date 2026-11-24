import os

import requests
from dotenv import load_dotenv
from flask import Flask, render_template, request

load_dotenv()

API_KEY = os.getenv("OMDB_API_KEY")
OMDB_URL = "https://www.omdbapi.com/"

ERRORS_KO = {
    "Movie not found!": "검색 결과가 없어요. 영어 제목으로 다시 검색해 보세요.",
    "Too many results.": "검색어가 너무 짧아요. 단어를 더 길게 입력해 보세요.",
    "Incorrect IMDb ID.": "영화 정보를 찾을 수 없어요.",
}

app = Flask(__name__)


def omdb(**params):
    """OMDb API를 호출하고 JSON 결과를 돌려준다."""
    if not API_KEY:
        return {"Response": "False", "Error": "API 키가 없어요. .env 파일에 OMDB_API_KEY를 입력해 주세요."}
    try:
        res = requests.get(OMDB_URL, params={"apikey": API_KEY, **params}, timeout=8)
        res.raise_for_status()
        return res.json()
    except requests.RequestException:
        return {"Response": "False", "Error": "OMDb 서버에 연결하지 못했어요. 잠시 후 다시 시도해 주세요."}


def translate_error(message):
    return ERRORS_KO.get(message, message)


@app.route("/")
def index():
    q = request.args.get("q", "").strip()
    page = max(request.args.get("page", 1, type=int), 1)
    movies, total, error = [], 0, None

    if q:
        data = omdb(s=q, type="movie", page=page)
        if data.get("Response") == "True":
            movies = data["Search"]
            total = int(data["totalResults"])
        else:
            error = translate_error(data.get("Error"))

    pages = (total + 9) // 10  # OMDb는 한 페이지에 10개
    return render_template("index.html", q=q, movies=movies, total=total,
                           page=page, pages=pages, error=error)


@app.route("/movie/<imdb_id>")
def movie(imdb_id):
    data = omdb(i=imdb_id, plot="full")
    if data.get("Response") == "True":
        return render_template("movie.html", m=data, error=None)
    return render_template("movie.html", m=None, error=translate_error(data.get("Error"))), 404


if __name__ == "__main__":
    app.run(debug=True)
