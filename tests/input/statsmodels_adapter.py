ID = "statsmodels_adapter"
TITLE = "Statsmodels results"
TAGS = ["statsmodels", "model"]
REQUIRES = ['statsmodels', 'numpy']
DISPLAY_INPUT = "sm.OLS(y, sm.add_constant(x)).fit()"
EXPECTED = "A statsmodels RegressionResultsWrapper with 2 params, R²=1."


def build():
    import numpy as np
    import statsmodels.api as sm

    x = np.arange(10)
    y = x * 2
    x = sm.add_constant(x)
    return sm.OLS(y, x).fit()
