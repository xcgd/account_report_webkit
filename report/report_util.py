def compare_ledger_types(account, data, orm):
    if not data['form']['ledger_type_available']:
        # Ignore this filter when alternate_ledger is not installed.
        return True

    selected_ledger = data['form']['ledger_type']
    account_ledgers = [ledger.id for ledger in account.ledger_types]

    if not selected_ledger:
        return account_ledgers == []

    return selected_ledger in account_ledgers


def should_show_account(account, data):
    if 'account_from' not in data['form'] or 'account_to' not in data['form']:
        return True

    low = data['form']['account_from']
    high = data['form']['account_to']

    return low <= account.code <= high


def should_show_line(line, currency_filter):
    return (
        not currency_filter or
        line.get('currency_id') == currency_filter
    )
