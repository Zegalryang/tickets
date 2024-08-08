import yaml

class ProductItem:
    def __init__(self, productId=None, showInfo={}, account={}) -> None:
        self.update(productId, showInfo, account)

    def update(self, productId, showInfo, account):
        self.productId = productId
        self.showInfo = showInfo
        self.account = account
        
class Items:
    __key_account = 'account'
    __key_showInfo = 'showInfo'
    __key_productId = 'productId'
    __key_userid = 'userid'
    __key_userpwd = 'userpwd'
    __key_productId = 'productId'
    __key_showInfo = 'showInfo'
    __key_month = 'month'
    __key_day = 'day'
    __key_seq = 'seq'

    items = []
    account = {}

    def __init__(self, account={}, items=[]) -> None:
        self.update(account, items)
    
    def update(self, account, items) -> None:
        self.account = account
        for item in items:
            _pid = None if not self.__key_productId in item else item[self.__key_productId]
            _si = {} if not self.__key_showInfo in item else item[self.__key_showInfo]
            _ac = {} if not self.__key_account in item else item[self.__key_account]

            self.items.append(ProductItem(
                productId=_pid,
                showInfo=_si,
                account=_ac))
        
    def userId(self, itemIndex=0) -> str:
        try:
            if self.account:
                return self.account[self.__key_userid]

            if len(self.items) < itemIndex: return None

            return self.items[itemIndex].account[self.__key_userid]

        except Exception as e:
            return None

    def userPwd(self, itemIndex=0) -> str:
        try:
            if self.account:
                return self.account[self.__key_userpwd]

            if len(self.items) < itemIndex: return None

            return self.items[itemIndex].account[self.__key_userpwd]

        except Exception as e:
            return None

    def productId(self, itemIndex=0) -> str:
        if len(self.items) < itemIndex: return None
        return self.items[itemIndex].productId
    
    def month(self, itemIndex=0) -> str:
        if len(self.items) < itemIndex: return None
        
        try:
            return str(self.items[itemIndex].showInfo[self.__key_month]).zfill(2)
        except Exception as e:
            print(f' * No exists month: {e}')

        return "01"
    
    def day(self, itemIndex=0) -> str:
        if len(self.items) < itemIndex: return None
        
        try:
            return str(self.items[itemIndex].showInfo[self.__key_day]).zfill(2)
        except Exception as e:
            print(f' * No exists day: {e}')

        return "01"
    
    def seq(self, itemIndex=0) -> str:
        if len(self.items) < itemIndex: return None
        
        try:
            return f'{self.items[itemIndex].showInfo[self.__key_seq]}회'
        except Exception as e:
            print(f' * No exists seq: {e}')

        return "1회"

with open('items.yaml', "r") as fp:
    e = yaml.safe_load(fp)

assert e, '🔥 items.yaml에 정보가 없음.'
info = Items(account=e['account'], items=e['items'])

assert (info.userId() and info.userPwd()), '🔥 사용자 정보가 없음.'
assert info.productId(), '🔥 상품 정보가 없음.'

print('📻 Ticketing info')
print(f'🔒 Account   : {info.userId()}. {len(info.userPwd())}')
print(f'🗞️ ProductID : {info.productId()}')
print(f'📅 Date      : {info.month()}. {info.day()}')
print(f'😃 회차       : {info.seq()}')