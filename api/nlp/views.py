from rest_framework.decorators import api_view
from rest_framework.response import Response
from games.serializers import GameSerializer
from games.models import Game
from .nlp.tf_idf import TFIDF


@api_view(["GET"])
def query(request):
    game_ids = []
    query = request.query_params.get("query")
    nlp_model = request.query_params.get("model")

    games = Game.objects.exclude(content="")

    if nlp_model == "tfidf" or True:
        corpus = [(game.appid, game.content) for game in games]
        tfidf = TFIDF(corpus)
        tfidf.fit_transform()
        game_ids, similarities = zip(*tfidf.get_similar_games(query, threshold=0.1))

    queryset = Game.objects.filter(appid__in=game_ids)
    serializer = GameSerializer(queryset, many=True)
    for game in queryset:
        serializer.data[game.appid]["similarity"] = similarities[
            game_ids.index(game.appid)
        ]

    return Response(serializer.data)
