
_API_MAP = {

    'current': {

        'version': '1.0',
        'api_version': 'v2-2.0.0',
        'api_root': 'http://dev.decktutor.com/ws-2.0/app/v2',
        'api_sandbox_root': 'http://dev.decktutor.com/ws-2.0/app/v2',
        'api': {

            'account': {

                'login': {
                    'url': '/account/login',
                    'description': 'Create a logged in user session to authenticate future requests',
                    'method': 'POST'
                }
            },
            'cdb': {

            },
            'handlings': {

            },
            'insertions': {

                'create': {
                    'url': '/insertions/create/{game}/{category}',
                    'description': 'Create a new insertion in a given category',
                    'methods': 'POST',
                    'resolver': 'decktutorsdk.resolvers.AuthResolver',
                },
                'info': {
                    'url': '/insertions/{code}/',
                    'description': 'Retrieve basic information about an insertion',
                    'methods': 'GET',
                    'resolver': 'decktutorsdk.resolvers.AuthResolver',
                },
                'page': {
                    'url': '/insertions/{code}/page',
                    'description': 'Retrieve all the information for an insertion',
                    'methods': 'GET',
                    'resolver': 'decktutorsdk.resolvers.AuthResolver',
                },
                'publish': {
                    'url': '/insertions/{code}/publish',
                    'description': 'Publish an unpublished insertion',
                    'methods': 'POST',
                    'resolver': 'decktutorsdk.resolvers.AuthResolver',
                },
                'publish_list': {
                    'url': '/insertions/{code}/publish',
                    'description': 'Publishes any number of insertions from the selling list',
                    'methods': 'POST',
                    'resolver': 'decktutorsdk.resolvers.AuthResolver',
                },
                'update': {
                    'url': '/insertions/{code}/field/{name}',
                    'description': 'Update one field of an existing insertion',
                    'methods': 'PUT',
                    'resolver': 'decktutorsdk.resolvers.AuthResolver',
                },
                'delete': {
                    'url': '/insertions/{code}/',
                    'description': 'Delete an existing insertion',
                    'methods': 'DELETE',
                    'resolver': 'decktutorsdk.resolvers.AuthResolver',
                },
                'messages': {
                    'url': '/insertions/{code}/publicMessages',
                    'description': 'Retrieve the list of public messages related to an insertion',
                    'methods': 'GET',
                    'resolver': 'decktutorsdk.resolvers.AuthResolver',
                },
                'create_message': {
                    'url': '/insertions/{code}/publicMessages',
                    'description': 'Post a public question or answer to an insertion',
                    'methods': 'POST',
                    'resolver': 'decktutorsdk.resolvers.AuthResolver',
                },
                'purchase': {
                    'url': '/insertions/{code}/purchase',
                    'description': 'Purchase an insertion',
                    'methods': 'POST',
                    'resolver': 'decktutorsdk.resolvers.AuthResolver',
                },
                'purchase_info': {
                    'url': '/insertions/purchases/',
                    'description': 'Retrieve the details of a previous purchase',
                    'methods': 'GET',
                    'resolver': 'decktutorsdk.resolvers.AuthResolver',
                },
            },
            'mytutor': {

                'set_seller_motd': {
                    'url': '/mytutor/setSellerMotd',
                    'description': 'Find card versions related to a specific card name or set',
                    'methods': 'GET',
                    'resolver': 'decktutorsdk.resolvers.AuthResolver',
                },
                'payment_methods': {
                    'url': '/mytutor/paymentMethods/{payment_id}',
                    'description': 'Find card versions related to a specific card name or set',
                    'method': 'GET',
                    'resolver': 'decktutorsdk.resolvers.AuthResolver',
                },
            },
            'search': {

                'card_name': {
                    'url': '/search/card/name',
                    'description': 'Find card versions related to a specific card name or set',
                    'methods': 'GET',
                    'resolver': 'decktutorsdk.resolvers.AuthResolver',
                },
                'list_categories': {
                    'url': '/search/set/{game}/{code}/categories',
                    'description': 'List available categories for a particular expansion set',
                    'methods': 'GET',
                    'resolver': 'decktutorsdk.resolvers.AuthResolver',
                },
                'list_filters': {
                    'url': '/search/category/{code}/filters',
                    'description': 'List all possible filters for a category including possible values',
                    'methods': 'GET',
                    'resolver': 'decktutorsdk.resolvers.AuthResolver',
                },
                'card_version': {
                    'url': '/search/card/version',
                    'description': 'Find products in a specific category',
                    'methods': 'GET',
                    'resolver': 'decktutorsdk.resolvers.AuthResolver',
                },
                'product_list': {
                    'url': '/search/products/{code}',
                    'description': 'Find card official names matching a text query',
                    'methods': 'GET',
                    'resolver': 'decktutorsdk.resolvers.AuthResolver',
                },
                'serp': {
                    'url': '/search/serp',
                    'description': 'Main search endpoint',
                    'methods': 'POST',
                    'resolver': 'decktutorsdk.resolvers.AuthResolver',
                },
                'self_serp': {
                    'url': '/search/self/serp',
                    'description': 'Search through the insertions database for own insertions',
                    'methods': 'POST',
                    'resolver': 'decktutorsdk.resolvers.AuthResolver',
                },
                'code': {
                    'url': '/search/insertion/code',
                    'description': 'Web service to autocomplete type-ahead',
                    'methods': 'GET',
                    'resolver': 'decktutorsdk.resolvers.AuthResolver',
                },
            },
            'sys': {

            },
            'users': {

            }
        }
    }
}

api_map = _API_MAP
