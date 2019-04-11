# all_data_sql = 'SELECT * FROM aplec_clue WHERE (DATE_SUB(CURDATE(),INTERVAL 1 WEEK) <= DATE(created)) AND ' \
#                '(code LIKE "%%LS:%%") OR (code LIKE "%%LA:%%") ORDER BY created DESC, probability DESC LIMIT %s, %s;'
#
# all_data_count_sql = 'SELECT count(*) FROM aplec_clue WHERE (DATE_SUB(CURDATE(),INTERVAL 1 WEEK) <= DATE(created)) AND ' \
#                      '(code LIKE "%%LS:%%") OR (code LIKE "%%LA:%%") ORDER BY created DESC, probability DESC;'
#
# search_sql = 'SELECT * FROM aplec_clue WHERE (DATE_SUB(CURDATE(),INTERVAL 1 WEEK) <= DATE(created)) AND ' \
#              '(aprus_id LIKE "%%' + aprus_id_keys + '%%") AND probability >= "' + probability_keys + '" AND ' \
#              '(code LIKE "%%LS:%%" OR code LIKE "%%LA:%%") ORDER BY created DESC, probability DESC ' \
#              'LIMIT ' + str(pages_count) + ', ' + str(items) + ';'
#
# search_count_sql = 'SELECT count(*) FROM aplec_clue WHERE (DATE_SUB(CURDATE(),INTERVAL 1 WEEK) <= DATE(created)) AND ' \
#                    '(aprus_id LIKE "%%' + aprus_id_keys + '%%") AND probability >= "' + probability_keys + '" AND ' \
#                    '(code LIKE "%%LS:%%" OR code LIKE "%%LA:%%") ORDER BY created DESC, probability DESC;'

