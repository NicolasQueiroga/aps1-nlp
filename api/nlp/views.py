from rest_framework.decorators import api_view
from rest_framework.response import Response
from games.models import Game
from .nlp.tf_idf import TFIDF


@api_view(["GET"])
def query(request):
    game_ids = []
    query = request.query_params.get("query")
    nlp_model = request.query_params.get("model")

    games = Game.objects.exclude(content="")

    if nlp_model == "tfidf":
        content = [game.content for game in games]
        tfidf = TFIDF()
        tfidf.fit_transform(content)
        game_ids = tfidf.get_similar_games(query, threshold=0.1)

    # response = Game.objects.filter(appid__in=game_ids)
    # serializer = GameSerializer(response, many=True)
    return Response(f"Query: {query}, Response: {game_ids}")
