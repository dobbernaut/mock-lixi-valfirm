from spyne import Application, rpc, Service, Iterable, Integer, Unicode, String, error, AnyXml
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication
from spyne.interface.wsdl.wsdl11 import Wsdl11
from spyne.model.complex import ComplexModel, ComplexModelBase

from validators import auth, message


class AuthHeader(ComplexModel):
    __tns__ = 'lixi.ab.valuations.services'
    UserName = Unicode
    Password = Unicode


class ABValuations(Service):
    __tns__ = 'lixi.ab.valuations.services'
    __in_header__ = AuthHeader

    @rpc(AnyXml, _returns=Unicode,  _out_variable_name='result')
    def order(ctx, ValuationMessage):
        validate_message(ctx.in_header.UserName, ctx.in_header.Password, ValuationMessage)
        return "0"


schema = './files/ValuationTransaction_1_6.xsd'


def validate_message(username, password, valuation_message):
    try:
        if not auth.authorized(username, password):
            raise error.InvalidCredentialsError()
        if not message.validate(valuation_message, schema):
            raise error.InvalidRequestError()
    except :
        raise error.InvalidInputError()


application = Application([ABValuations], 'lixi.ab.valuations.services',
                          in_protocol=Soap11(validator='lxml'),
                          out_protocol=Soap11(polymorphic=True))

wsgi_application = WsgiApplication(application)


if __name__ == '__main__':
    import logging

    from wsgiref.simple_server import make_server

    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger('spyne.protocol.xml').setLevel(logging.DEBUG)
    logging.info("listening to http://127.0.0.1:8000")
    logging.info("wsdl is at: http://localhost:8000/?wsdl")

    server = make_server('127.0.0.1', 8000, wsgi_application)
    server.serve_forever()
