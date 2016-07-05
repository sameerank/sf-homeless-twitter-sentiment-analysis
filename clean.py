import pandas as pd
df = pd.read_csv('sfhomeless.csv')

from textblob import TextBlob
df['polarity'] = df.apply(lambda x: TextBlob(x['Text']).sentiment.polarity, axis=1)
df['subjectivity'] = df.apply(lambda x: TextBlob(x['Text']).sentiment.subjectivity, axis=1)

from dateutil.parser import parse
df['DateCreated'] = df.apply(lambda x: parse(x['DateCreated']), axis=1)
df.sort_values(by=['DateCreated'], inplace=True)

output_file = open('sfHomelessData.js', 'w')
output_file.write('var sfHomelessData = [\n')

for i in range(df.shape[0]):
    new_date = df.iloc[i].DateCreated
    new_line = ("\t[new Date(" + str(new_date.year)
    + ", " + str(new_date.month) + ", " + str(new_date.day)
    + ", " + str(new_date.hour)
    + ", " + str(new_date.minute)
    + ", " + str(new_date.second) + ").getTime()"
    + ", " + str(df.iloc[i].polarity)
    + ", " + str(df.iloc[i].subjectivity) + "],\n")
    output_file.write(new_line)

output_file.write(']')
output_file.close
