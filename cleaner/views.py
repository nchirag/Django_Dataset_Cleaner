from django.shortcuts import render
from .models import *
import pandas as pd

# Create your views here.
def home(request):
    return render(request,'index.html')

def cleaning(request):
    return render(request,'cleaning.html')

def upload_file(request):
    if request.method == 'POST' and request.FILES.get('file'):
        uploaded_file = request.FILES['file']
        file_instance = File(file=uploaded_file)
        file_instance.save()
        return render(request,'cleaning.html',{"message":"File uploaded successfully"})
    return render(request,'cleaning.html')

def dataset_description(request):
    latest_file = File.objects.last()
    if not latest_file:
        return render(request, 'cleaning.html', {"message": "No file uploaded yet"})
    
    file_path = latest_file.file.path
    try:
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        else:
            return render(request, 'cleaning.html', {'message': 'File format not supported'})
        
        # Perform statistical analysis
        stats = df.describe()

        # Convert the statistics to a list of dictionaries for rendering
        description = []
        for column in stats.columns:
            description.append({
                "column": column,
                "count": stats.loc["count", column],
                "mean": stats.loc["mean", column],
                "std": stats.loc["std", column],
                "min_value": stats.loc["min", column],
                "percentile_25": stats.loc["25%", column],
                "percentile_50": stats.loc["50%", column],
                "percentile_75": stats.loc["75%", column],
                "max_value": stats.loc["max", column],
            })
        DatasetStatistics.objects.create(
            file=latest_file,
            count=description[0]["count"],
            mean=description[0]["mean"],
            std=description[0]["std"],
            min_value=description[0]["min_value"],
            percentile_25=description[0]["percentile_25"],
            percentile_50=description[0]["percentile_50"],
            percentile_75=description[0]["percentile_75"],
            max_value=description[0]["max_value"],
        )

        return render(request, 'cleaning.html', {"description": description})
    except Exception as e:
        return render(request, 'cleaning.html', {"message": f"Error processing file: {str(e)}"})
