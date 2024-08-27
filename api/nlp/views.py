from rest_framework.decorators import api_view
from rest_framework.response import Response
from games.models import Game
from .nlp.tf_idf import TFIDF


@api_view(["GET"])
def query(request):
    query = request.query_params.get("query")
    games = Game.objects.all()

    response = []
    return Response(f"Query: {query}, Response: {response}")
