# vim: set encoding=utf-8 et sw=4 sts=4 :

from error import Error

import logging 
log = logging.getLogger('dispatcher')


class Dispatcher(object):
    _actions  = {}

    def __init__(self):
        log.debug('Dispatcher()')
        self.register_action('help', self._action_help)

    def register_action(self, action, callback):
        if action in self._actions:
            raise AlreadyRegisteredActionError(action)
        log.debug(u'register_action(): %s' % (action,))
        self._actions[action] = callback

    def dispatch(self, msg):
        (action, params) = self._parse_msg(msg)
        log.debug(u'dispatch(): %s' % (action,))
        if not self._actions[action]:
            raise InvalidActionError(action)
        return self._actions[action](params=params)

    def _parse_msg(self, msg):
        msg = msg.strip()
        log.debug(u'_parse_msg(): %s, TODO: Repensar esto' % (msg,) )
        (action, sep, params) = msg.partition(' ')
        return (action, params.split(','))

    def _action_help(self, params):
        """This message
        """
        response = u"------------------------\n"
        response+= u"Available actions with their description"
        for k in self._actions:
            response+= u"\n- %s : %s" %(k, self._actions[k].__doc__)
        response+= u"\n------------------------\n"
        return response


class AlreadyRegisteredActionError(Error):
    """Raised when an action is already registered.
    """
    pass

class InvalidActionError(Error):
    """Raised when the action is not registered.
    """
    pass
