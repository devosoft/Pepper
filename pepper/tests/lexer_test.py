import pepper.lexer as lexer

def get_all_tokens(given_lexer):
  tokens = []
  while True:
    tok = given_lexer.token()
    if not tok:
      break
    tokens.append(tok)

  return tokens


def test_lexer_basic_example():
  test_lines = open('pepper/tests/test_data/example.cpp', 'r').readlines()
  lexer.lexer.input('\n'.join(test_lines))
  tokens = get_all_tokens(lexer.lexer)

  assert(len(tokens) == 5)
