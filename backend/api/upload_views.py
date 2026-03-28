import os
from rest_framework.views import APIView
from rest_framework.response import Response
from uploadthing_py import create_uploadthing, create_route_handler

# 1. Define the File Router
f = create_uploadthing()

upload_router = {
    "videoUploader": f({
        "video": {"max_file_size": "128MB"}
    })
    .on_upload_complete(lambda file, metadata: print(f"Upload complete: {file.url}"))
}

# 2. Create the Route Handler
handlers = create_route_handler(
    router=upload_router,
    api_key=os.getenv("UPLOADTHING_TOKEN"),
    is_dev=os.getenv("DEBUG", "True") == "True",
)

class UploadThingView(APIView):
    def get(self, request):
        # The frontend SDK calls GET to fetch the router configuration
        slug = request.GET.get('slug')
        action_type = request.GET.get('actionType')
        
        # Pass the query params to the handler
        res = handlers["GET"](request.GET.dict())
        return Response(res)

    def post(self, request):
        # The frontend SDK calls POST to generate presigned URLs
        # We need to pass the request data and headers
        res = handlers["POST"](request.data, request.headers)
        return Response(res)
