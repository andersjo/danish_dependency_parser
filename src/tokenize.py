# coding: utf-8
import codecs
import re

# Handle smileys

class DanishTokenizer(object):
    word_begin_chars = set(u'-\[{(`"‚„†‡‹‘’“”•–—›««\'')
    word_end_chars = set(u'-\]}\'\`"),;:\!\?\%‚„…†‡‰‹‘’“”•–—›»')
    # around_word_chars = word_begin_chars | word_end_chars
    quote_chars = set(u'\'`")‹‘’“”›»««')


    def __init__(self, abbrevations):
        self.abbr_pattern = self._compile_abbrevations_re(abbrevations)
        # TODO define using unicode character ranges
        self.word_pattern = re.compile(u"[^–—;’‘‚”“„‡†•%'…)(«\-,‰‹»›?!\"\[\]`:\{\}\s\.]+", re.IGNORECASE)
        self.url_pattern = re.compile(r"(http(s)?://)?([\w-]+\.)+[\w-]+(/[;,./?%&=\w]*)?")
        self.clitic_pattern = re.compile(r"'s|'", re.IGNORECASE)

        # print "".join(self.around_word_chars)
        # self.around_word_pattern = re.compile(r)


    def _compile_abbrevations_re(self, abbrevations):
        parts = []
        for abbr in abbrevations:
            # Allow space after internal punctuation in the abbrevation
            abbr = re.sub(r"\.(?!$)", "\\.\\s*", abbr)
            abbr = re.sub(r"\.$", "\.", abbr)
            parts.append(abbr)

        pattern = u"({})".format(u"|".join(parts))
        return re.compile(pattern)

    def tokenize(self, text):
        tokens = []
        remaining = text

        while remaining:
            read = 0
            first_char = remaining[0]
            if first_char.isspace():
                read = 1
            else:
                for pattern in [self.abbr_pattern, self.url_pattern, self.clitic_pattern, self.word_pattern]:
                    m = pattern.match(remaining)
                    if m:
                        word = m.group(0)
                        read = len(word)
                        tokens.append(word)
                        break

                if read == 0:
                    tokens.append(first_char)
                    read = 1

            remaining = remaining[read:]

        return tokens

    def sent_tokenize(self, text):
        tokens = self.tokenize(text)
        split_at = []

        for i in range(1, len(tokens)-1):
            cur = tokens[i]
            next = tokens[i+1]
            next_next = tokens[i+2] if len(tokens) > i+2 else None

            if cur == '?' or cur == '!' or cur == '...':
                next_is_upper = next[0].isupper()
                next_next_is_quoted_and_upper = next in self.quote_chars and next_next and next_next[0].isupper()
                if next_is_upper or next_next_is_quoted_and_upper:
                    split_at.append(i)
            elif cur == '.':
                split_at.append(i)

        sentences = []
        slices = [-1] + split_at + [len(tokens)]
        for start, end in zip(slices, slices[1:]):
            sentences.append(tokens[start+1:end+1])

        return sentences

def read_abbrevations(filename):
    return [line.strip() for line in codecs.open(filename)]
