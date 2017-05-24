import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.iostream
import os

from log_handlers import *
from customer_handlers import *
from waiter_handlers import *
from cook_handlers import *
from manager_handlers import *
from tornado.options import define, options

define("port", default=8000, help="run on the given port", type=int)
define("debug", default=False, help="run in debug mode")



myhandlers = [(r'/', EntryHandler),
              (r'/faculty-login', FacultyLoginHandler),
              (r'/faculty-logout', FacultyLogoutHandler),
              (r'/faculty-home', FacultyHomeHandler),
              (r'/customer-category', CustomerCategoryHandler),
              (r'/customer-category-logout', CustomerCategoryLogoutHandler),
              (r'/customer-category-transfer', CustomerCategoryTransferHandler),
              (r'/customer-category-request', CustomerCategoryRequestHandler),
              (r'/customer-order-update', CustomerOrderUpdateHandler),
              (r'/customer-make-order', CustomerMakeOrderHandler),
              (r'/customer-detail', CustomerDetailHandler),
              (r'/customer-detail-transfer', CustomerDetailTransferHandler),
              (r'/customer-overlay', CustomerOverlayHandler),
              (r'/customer-order', CustomerOrderHandler),
              (r'/customer-history', CustomerHistoryHandler),
              
              (r'/waiter-request', WaiterRequestHandler),
              (r'/waiter-customer-request-update', WaiterCustomerRequestUpdateHandler),
              (r'/waiter-customer-submit-update', WaiterCustomerSubmitUpdateHandler),
              (r'/waiter-cook-request-update', WaiterCookRequestUpdateHandler),
              (r'/waiter-category', WaiterCategoryHandler),
              (r'/waiter-category-login', WaiterCategoryLoginHandler),
              (r'/waiter-category-logout', WaiterCategoryLogoutHandler),

              (r'/waiter-category-to-detail', WaiterCategoryToDetailHandler),
              (r'/waiter-detail', WaiterDetailHandler),
              (r'/waiter-detail-order', WaiterDetailOrderHandler),

              (r'/waiter-order', WaiterOrderHandler),
              (r'/waiter-order-order', WaiterOrderOrderHandler),

              (r'/waiter-order-update', WaiterOrderUpdateHandler),
              (r'/waiter-search', WaiterSearchHandler),
              (r'/waiter-transfer', WaiterTransferHandler),
              (r'/waiter-transfer-answer', WaiterTransferAnswerHandler),
              (r'/waiter-transfer-update', WaiterTransferUpdateHandler),

              (r'/cook-cook', CookCookHandler),
              (r'/cook-instruction', CookInstructionHandler),
              (r'/cook-cook-pad', CookCookPadHandler),
              (r'/cook-cook-other-pad', CookCookOtherPadHandler),
              (r'/cook-cook-phone', CookCookPhoneHandler),
              (r'/cook-cook-other-phone', CookCookOtherPhoneHandler),
              (r'/cook-call', CookCallHandler),
              (r'/manager', ManagerHandler),
              (r'/company-info', CompanyInfoHandler),
              (r'/company-data', CompanyDataHandler),
              (r'/category-manage', CategoryManageHandler),
              (r'/category-add', CategoryAddHandler),
              (r'/diet-manage', DietManageHandler),
              (r'/diet-add', DietAddHandler),
              (r'/desk-add', DeskAddHandler),
              (r'/desk-manage', DeskManageHandler),
              (r'/qrcode-download', QrcodeDownloadHandler),
              (r'/faculty-manage', FacultyManageHandler),
              (r'/faculty-add', FacultyAddHandler),
              (r'/history-data', HistoryDataHandler)
              ]

settings = dict(
                cookie_secret="__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",
                login_url="/",
                template_path=os.path.join(os.path.dirname(__file__), "templates"),
                static_path=os.path.join(os.path.dirname(__file__), "static"),
                xsrf_cookies=False,
                debug=options.debug,
                )


def main():
    tornado.options.parse_command_line()
    application = tornado.web.Application(myhandlers, **settings)
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
