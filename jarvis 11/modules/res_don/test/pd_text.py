import pandas as pd
import numpy as np
from collections import Counter
import matplotlib.pyplot as plt
import re

# Read the text file
with open('example/sample.txt', 'r') as file:
    text = file.read()

# Split text into sentences
sentences = re.split(r'[.!?]+', text)
sentences = [s.strip() for s in sentences if s.strip()]

# Create a DataFrame with sentences
df_sentences = pd.DataFrame(sentences, columns=['sentence'])
df_sentences['word_count'] = df_sentences['sentence'].apply(lambda x: len(x.split()))
df_sentences['char_count'] = df_sentences['sentence'].apply(len)

# Basic statistics
print("\nText Analysis Statistics:")
print(f"Total number of sentences: {len(sentences)}")
print(f"Average words per sentence: {df_sentences['word_count'].mean():.2f}")
print(f"Average characters per sentence: {df_sentences['char_count'].mean():.2f}")

# Word frequency analysis
words = re.findall(r'\b\w+\b', text.lower())
word_freq = Counter(words)

# Create DataFrame of word frequencies
df_words = pd.DataFrame.from_dict(word_freq, orient='index', columns=['frequency'])
df_words = df_words.sort_values('frequency', ascending=False)

print("\nTop 10 most frequent words:")
print(df_words.head(10))

# Plot word frequency distribution
plt.figure(figsize=(12, 6))
df_words.head(15)['frequency'].plot(kind='bar')
plt.title('Top 15 Word Frequencies')
plt.xlabel('Words')
plt.ylabel('Frequency')
plt.xticks(range(15), df_words.head(15).index, rotation=45)
plt.tight_layout()
plt.savefig('example/word_frequency_plot.png')
plt.close()

# Sentence length distribution
plt.figure(figsize=(10, 6))
df_sentences['word_count'].hist(bins=20)
plt.title('Distribution of Sentence Lengths')
plt.xlabel('Number of Words')
plt.ylabel('Frequency')
plt.tight_layout()
plt.savefig('example/sentence_length_plot.png')
plt.close()

# Section analysis
sections = text.split('\n\n')
df_sections = pd.DataFrame(sections, columns=['content'])
df_sections['section_length'] = df_sections['content'].apply(len)
df_sections['section_words'] = df_sections['content'].apply(lambda x: len(re.findall(r'\b\w+\b', x)))

print("\nSection Analysis:")
print(f"Number of sections: {len(sections)}")
print("\nSection lengths (in words):")
print(df_sections[['section_words']].describe())

# Export processed data
df_words.to_csv('example/word_frequencies.csv')
df_sentences.to_csv('example/sentence_analysis.csv')
df_sections.to_csv('example/section_analysis.csv')