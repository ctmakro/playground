'''
reputation_factor of a voting user is mainly determined by his reputation.

reputation > 30 => 1
otherwise => 0

'''
# https://github.com/pincong/pincong-wecenter/blob/master/models/vote.php
# on upvote:
def agree(type, factor, affect_currency, item_id, uid):
    # type: what's being upvoted on
    # factor: reputation_factor of the voting user*
    # affect: whether this affects the credits
    # item_id: the post being voted on
    # item_uid: the user being voted on
    # uid: they user who voted

    if type in [question,answer,article,comment,video,comment]:
        return False

    # see if voted already
    voteinfo = SQL('select * from vote where type=type and item_id=item_id and uid=uid')

    # update vote info if necessary
    if not voteinfo:
        'insert newvote() into vote'

        increase_count_and_rep(type, iid, uid, iuid, factor)
        process_currency_agree(type, iid, uid, iuid, affect_currency)
        return True

    else:

        vote_value = voteinfo['value'] # num of votes on a certain item by a certain user

    increase_count_and_rep() # or decrease, but i don't get why two separate functions
    process_currency_agree()


def increase_count_and_rep(type, iid, uid, iuid, factor):

    iteminfo = get_thread_or_reply_info_by_id(type, iid)

    # give you bonus if the wordcount is large.
    reputation = float(get_bonus_reputation(type, iid, factor, iteminfo))

    #...

    # discount your reputation if you upvote too much this week.
    reputation = calc_upvote_reputation(uid, reputation)

    # add reputation to your account.
    update_user_agree_count_and_reputation(iuid, 1, reputation)

def get_bonus_reputation(type, iid, factor, iteminfo):
    bonus_factor = get_setting('bonus_factor')

    bonus_min_count = gs('bonus_min_count')
    bonus_max_count = gs('bonus_max_count')

    if not bonus_factor:
        return factor # default is 1

    # bonus_factor is a number

    wordcount = int(len(post_being_voted_on)/3) # UTF-8

    if wordcount<bonus_min_count:
        return factor # default is 1

    sigmoid = 1/(1+exp(-6*((wordcount - bonus_min_count)/bonus_max_count - 0.5)))

    factor = bonus_factor* .5 * (1+sigmoid) * factor

    if wordcount < bonus_max_count/2:
        factor = factor *.5

    factor = round(factor, 6)

    return factor

def calc_upvote_reputation(uid, reputation):
    arg = get_setting('reputation_dynamic_weight_agree') # the fuck is that

    if arg is not None:
        reputation = calc_dynamic_reputation(reputation, arg, get_user_upvotes_last_week($uid));

    return reputation # do nothing if arg is null


# drep = rep * e^(-weight * posts_last_week)
# if weight = 0, drep = rep
# assume weight == 1(0.1)
# plw == 1 => drep = rep*0.37(0.90)
# plw == 2 => drep = rep*0.14(0.82)
# plw == 3 => drep = rep*0.05(0.74)

def calc_dynamic_reputation(reputation, arg, total):
    if total>0:
        reputation = reputation * exp(-arg*total)
    return reputation
