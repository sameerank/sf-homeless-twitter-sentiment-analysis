import pandas as pd
df = pd.read_csv('sfhomeless.csv')

from textblob import TextBlob
df['polarity'] = df.apply(lambda x: TextBlob(x['text']).sentiment.polarity, axis=1)
df['subjectivity'] = df.apply(lambda x: TextBlob(x['text']).sentiment.subjectivity, axis=1)

from dateutil.parser import parse
df['created_at'] = df.apply(lambda x: parse(x['created_at']), axis=1)
df.sort_values(by=['created_at'], inplace=True)

from difflib import SequenceMatcher
def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

cleaned_data = []
visited = set()
for i in range(df.shape[0]):
    if i not in visited:
        cleaned_data.append({
        'created_at': df.iloc[i].created_at
        , 'polarity': df.iloc[i].polarity
        , 'subjectivity': df.iloc[i].subjectivity
        , 'count': 0
        , 'text': df.iloc[i].text.replace("'","").replace('"',"").replace('\n', ' ').replace('\r', '')
        })
    for j in range(i + 1, df.shape[0]):
            if j not in visited and similar(df.iloc[i].text, df.iloc[j].text) > 0.5:
                visited.add(j)
                cleaned_data.append({
                    'created_at': df.iloc[j].created_at
                    , 'polarity': df.iloc[j].polarity
                    , 'subjectivity': df.iloc[j].subjectivity
                    , 'count': cleaned_data[-1]['count'] + 1
                    , 'text': df.iloc[i].text.replace("'","").replace('"',"").replace('\n', ' ').replace('\r', '')
                })

output_file = open('sfHomelessData.js', 'w')
output_file.write('var sfHomelessData = [\n')

for i in range(len(cleaned_data)):
    new_date = cleaned_data[i]['created_at']
    new_line = ('\t[new Date(' + str(new_date.year)
    + ', ' + str(new_date.month) + ', ' + str(new_date.day)
    + ', ' + str(new_date.hour)
    + ', ' + str(new_date.minute)
    + ', ' + str(new_date.second) + ').getTime()'
    + ', ' + str(cleaned_data[i]['polarity'])
    + ', ' + str(cleaned_data[i]['subjectivity'])
    + ', ' + str(cleaned_data[i]['count'])
    + ', "' + str(cleaned_data[i]['text']) + '"],\n')
    output_file.write(new_line)

output_file.write(']')
output_file.close
