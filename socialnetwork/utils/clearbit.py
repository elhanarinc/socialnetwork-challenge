import clearbit

clearbit.key = 'sk_a069723050fa21735afd631958e6ab1a'


def find_extensive_data(email):
    response = clearbit.Enrichment.find(email=email, stream=True)
    return response
