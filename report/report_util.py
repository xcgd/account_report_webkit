def compare_ledger_types(account, data, orm):
    # TODO alternate_ledger
    return True

    account_ledgers = [ledger.id for ledger in account.ledger_types]
    selected_ledger = int(data['form']['ledger_type'])

    # Store in data to avoid recomputing.
    if 'ledger_type_all' not in data:
        data['ledger_type_all'] = (
            orm.pool.get('alternate_ledger.ledger_type').browse(
                orm.cursor, orm.uid, selected_ledger).name == 'A')
    catch_all = data['ledger_type_all']

    return (selected_ledger in account_ledgers or
            (catch_all and account_ledgers == []))

def should_show_account(account, data):
    if 'account_from' not in data['form'] or 'account_to' not in data['form']:
        return True

    low = data['form']['account_from']
    high = data['form']['account_to']

    return low <= account.code <= high
