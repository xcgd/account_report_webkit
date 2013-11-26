def compare_ledger_types(account, data, orm):
    account_ledgers = [ledger.id for ledger in account.ledger_types]
    selected_ledgers = data['form']['ledger_types']

    # Store in data to avoid recomputing.
    if 'ledger_type_all' not in data:
        ledger_A = orm.pool.get('alternate_ledger.ledger_type').search(
            orm.cursor, orm.uid, [('name', '=', 'A')]
        )
        data['ledger_type_all'] = (
            ledger_A and
            ledger_A[0] in selected_ledgers
        )
    catch_all = data['ledger_type_all']

    if catch_all and account_ledgers == []:
        return True

    for selected_ledger in selected_ledgers:
        if selected_ledger in account_ledgers:
            return True

    return False

def should_show_account(account, data):
    if 'account_from' not in data['form'] or 'account_to' not in data['form']:
        return True

    low = data['form']['account_from']
    high = data['form']['account_to']

    return low <= account.code <= high
