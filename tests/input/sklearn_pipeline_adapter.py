ID = "sklearn_pipeline_adapter"
TITLE = "Sklearn pipeline"
TAGS = ["sklearn", "pipeline"]
REQUIRES = ['sklearn']
DISPLAY_INPUT = "Pipeline([('imputer', SimpleImputer()), ('scaler', StandardScaler())])"
EXPECTED = (
    "A unfitted sklearn Pipeline with 2 steps:\n"
    "1. 'imputer': SimpleImputer\n"
    "2. 'scaler': StandardScaler\n"
    "Expects input shape (*, ?), outputs class predictions."
)


def build():
    from sklearn.impute import SimpleImputer
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import StandardScaler

    return Pipeline(
        [
            ("imputer", SimpleImputer()),
            ("scaler", StandardScaler()),
        ]
    )
