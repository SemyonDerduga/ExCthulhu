from cthulhu_src.services.exchangers.base_exchanger import BaseExchanger


class Yobit(BaseExchanger):
    name = 'yobit'
    opts = {
        'enableRateLimit': True,
    }
