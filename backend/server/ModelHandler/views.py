from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
# from .models import UploadedPDF  # if using model
# from .serializers import UploadedPDFSerializer  # if using model
# from .extraction_model import extract_data_from_pdf  # your extraction function

class PDFUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)  # for file uploads

    def post(self, request, format=None):
        file_obj = request.FILES.get('file')
        if not file_obj:
            return Response({"error": "No file provided."}, status=status.HTTP_400_BAD_REQUEST)

        # If you want to save it:
        # serializer = UploadedPDFSerializer(data={'file': file_obj})
        # if serializer.is_valid():
        #     pdf_instance = serializer.save()
        # else:
        #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Extract data using your model
        # extracted_data = extract_data_from_pdf(file_obj)

        return Response({
            "message": "File processed successfully",
            # "data": extracted_data
        }, status=status.HTTP_200_OK)