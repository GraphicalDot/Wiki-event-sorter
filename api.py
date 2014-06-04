#!/usr/bin/env python
from flask import Flask
from flask.ext.restful import Api, Resource, reqparse
import wikipedia
from simple_tokenization import return_data
app = Flask(__name__)
api = Api(app)


class SampleResource(Resource):
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('query', required=True, type=str, location='args')

    def get(self):
        # parse arguments
        args = self.get_parser.parse_args()
	try: 
		query = wikipedia.page(args.get("query"))
		data = return_data(query)
		return {"data": data,
			"error": False,
			"success": True,}
	except wikipedia.DisambiguationError as e:
		return {"data": e,
				"error": True	}


api.add_resource(SampleResource, '/get_resource')


if __name__ == "__main__":
	app.run(host="0.0.0.0", port=5000, debug=True)
