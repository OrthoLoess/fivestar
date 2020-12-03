import joblib


class Model():


    def predict(self, X_new):
        y_pred = self.pipeline.predict(X_new)
        return y_pred


    def load_model(self):
        self.pipeline = joblib.load('model.joblib')
        return self
