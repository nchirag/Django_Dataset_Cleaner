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

        # Load the uploaded file into a pandas DataFrame
        try:
            file_path = file_instance.file.path
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            else:
                return render(request, 'cleaning.html', {"message": "File format not supported"})

            # Store dataset preview in session
            request.session['dataset_preview'] = df.head().to_html(classes='table table-bordered', index=False)

            return render(request, 'cleaning.html', {
                "message": "File uploaded successfully",
                "dataset_preview": request.session['dataset_preview']
            })
        except Exception as e:
            return render(request, 'cleaning.html', {"message": f"Error processing file: {str(e)}"})

    return render(request, 'cleaning.html')




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

        description = []
        for column in stats.columns:
            description.append({
                "column": column,
                "count": int(stats.loc["count", column]),
                "mean": round(stats.loc["mean", column], 2),
                "std": round(stats.loc["std", column], 2),
                "min_value": round(stats.loc["min", column], 2),
                "percentile_25": round(stats.loc["25%", column], 2),
                "percentile_50": round(stats.loc["50%", column], 2),
                "percentile_75": round(stats.loc["75%", column], 2),
                "max_value": round(stats.loc["max", column], 2),
            })

        # 🔹 Call detect_issues function and get issues
        issues = detect_issues(df, latest_file)  # Call helper function
        
    

        return render(request, 'cleaning.html', {
            "description": description,
            "issues": issues  # Pass issues to template
        })
    except Exception as e:
        return render(request, 'cleaning.html', {"message": f"Error processing file: {str(e)}"})



def detect_issues(df, latest_file):
    issues = []
    
    for column in df.columns:
        column_issues = []

        # ✅ Store column data type as a string
       

        # ✅ Check for missing values
        missing_count = int(df[column].isnull().sum())  
        if missing_count > 0:
            column_issues.append({
                "column": column,  
                "issue_type": "Missing values",  
                "value": missing_count  
            })

        # ✅ Check for duplicates
        duplicate_count = int(df.duplicated(subset=[column]).sum())  
        if duplicate_count > 0:
            column_issues.append({
                "column": column,  
                "issue_type": "Duplicate values",  
                "value": duplicate_count  
            })

        # ✅ Check for outliers (Only for numeric columns)
        if pd.api.types.is_numeric_dtype(df[column]):
            q1 = df[column].quantile(0.25)
            q3 = df[column].quantile(0.75)
            iqr = q3 - q1
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            outlier_count = int(((df[column] < lower_bound) | (df[column] > upper_bound)).sum())  
            if outlier_count > 0:
                column_issues.append({
                    "column": column,  
                    "issue_type": "Outliers",  
                    "value": outlier_count  
                })

        # ✅ Save detected issues to the database
        if column_issues:
            issues.extend(column_issues)

            for issue in column_issues:
                DetectedIssue.objects.create(
                    file=latest_file,
                    column=issue["column"],  # Ensure column name is stored
                    issue_type=issue["issue_type"],
                    value=int(issue["value"]),  
                )


    return issues  
