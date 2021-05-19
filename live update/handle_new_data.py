import csv
import pickle
import pandas as pd

class HandleData:
    def __init__(self, param_dict):
        self.running_preds = pd.DataFrame()
        self.target = param_dict['target']
        self.model_file = param_dict['model_file']
        self.file_id = self.model_file.split('.')[0]
        self.end_row = len(param_dict['symbols'])-1


    def data_triage(self, dict):
        # write raw data to csv
        self.write_mktdata_to_csv(dict)

        # create dataframe and make new prediction with it
        new_df = self.make_new_prediction(self.create_dataframe(dict))

        #add new prediction to running data
        running_df = self.add_to_running_stats(new_df)

        # output running data to csv
        self.write_predictions_to_csv(running_df)


    def write_mktdata_to_csv(self, dict):

        with open(self.file_id + '_DataOutput.csv', 'a', newline='') as csv_a, open(self.file_id + '_DataOutput.csv','r', newline='') as csv_r:
            reader = csv.reader(csv_r)
            writer = csv.DictWriter(csv_a, dict.keys())
            # put each row into a dict
            data = [row for row in reader]

            # check to see if 2nd row is blank(since newline puts first entry on 2nd row)
            try:
                first_row_blank = True if data[1] == [] else False

            except IndexError:
                first_row_blank = True

            if first_row_blank:
                writer.writeheader()
                writer.writerow(dict)
            else:
                writer.writerow(dict)

    def write_predictions_to_csv(self, df):

        with open(self.file_id + '_Predictions.csv', 'a', newline='') as csv_a, open(self.file_id + '_Predictions.csv','r', newline='') as csv_r:
            reader = csv.reader(csv_r)
            data = [row for row in reader]

            try:
                first_row_blank = True if data[1] == [] else False

            except IndexError:
                first_row_blank = True

            if first_row_blank:
                df.iloc[-1:].to_csv(csv_a, header=True)
            else:
                df.iloc[-1:].to_csv(csv_a, header=False)


    def create_dataframe(self, dict):
        df = pd.DataFrame([dict])
        df['Timestamp'] = pd.to_datetime(df['Timestamp']) + pd.Timedelta(hours=1, minutes=30)
        df.set_index('Timestamp', inplace=True)

        return df

    def make_new_prediction(self, df):
        model = pickle.load(open(self.model_file, 'rb'))

        X = df.iloc[:, 0:self.end_row]

        y_pred = model.predict(X)
        df['y_pred'] = y_pred
        # self.add_to_running_stats(df)
        return df

    def add_to_running_stats(self, df):
        self.running_preds = self.running_preds.append(df, sort=False)
        self.running_preds['ModelDiff'] = self.running_preds['y_pred']-self.running_preds[self.target]
        self.running_preds['ModelDelta'] = round((self.running_preds['y_pred'] - self.running_preds['y_pred'].shift(1)),2)
        self.running_preds[self.target+'Delta'] = round((self.running_preds[self.target]-self.running_preds[self.target].shift(1)),2)
        self.running_preds['PeriodDiff'] = round(self.running_preds['ModelDelta'] - self.running_preds[self.target+'Delta'],2)
        return self.running_preds
        # self.write_predictions_to_csv(self.running_preds)



