user_actions = []
context_roots = []

filename = 'customer_specific/new_relic_query1.txt'
with open(filename, 'r') as f:
    str = f.read()
    # print(str)
    query_tokens = str.split(' ')
    # print(query_tokens)
    for token in query_tokens:
        if '%' in token:
            token = token.replace("'", "")
            token = token.replace("%", "")
            # print(token)
            if token != '"buttonClicked":"Edit"' and token != '/overview':
                user_actions.append(token)

            ua_split = token.split('/')[0]
            if ua_split not in context_roots:
                if ua_split != '"buttonClicked":"Edit"' and ua_split > '':
                    context_roots.append(ua_split)

        # if token not in all_query_tokens:
        #     add_relevant_token(token)

    print('User Actions:')
    for userAction in sorted(user_actions):
        print(userAction)

    print('')
    print('Context Roots:')
    for context_root in context_roots:
        print(context_root)
