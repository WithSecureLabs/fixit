"""
fixit_message_creator.py

Part of the Fixit Project
WithSecure Labs (c) 2024

Description:
    This module defines the `MessageCreator` class, which provides functionality for generating
    FIX message templates. It is used when users have no predefined messages to import but need
    to quickly create example FIX messages for testing or interaction with a FIX gateway.

Key Features:
    - Creates FIX messages with standard headers and required fields.
    - Supports multiple message types, including:
        - Logon (A)
        - TestRequest (1)
        - NewOrderSingle (D)
        - OrderCancelRequest (F)
        - OrderStatusRequest (H)
        - QuoteRequest (R)
        - MarketDataRequest (V)
    - Ensures compatibility with the QuickFIX library and FIX protocol versions.

Usage:
    The `MessageCreator` class is designed to be used within the Fixit application.
    Example:
        ```python
        msg = MessageCreator.NewOrderSingle(context, sessionID, "AAPL", 100, 150.0, fix.Side_BUY)
        ```
    These methods return FIX message objects that can be sent directly through the FIX gateway.
"""

from quickfix import FieldNotFound

from fixit.utils.exceptions import InvalidArgsError

#pylint: disable=wildcard-import,unused-wildcard-import
import quickfix as fix
import quickfix44 as fix44
from fixit.core.constants import *

class MessageCreator():
    """
    Provides static methods to create various types of FIX messages for the Fixit application.

    The `MessageCreator` class simplifies the process of generating FIX messages with standard
    headers and fields, enabling users to test and interact with FIX gateways.
    """

    @staticmethod
    def gen_new_message(context, sessionID):
        """
        Creates a new FIX message with standard headers.

        Args:
            context (object): The application context containing session details.
            sessionID (object): The session ID for the FIX connection.

        Returns:
            fix.Message: A FIX message object with standard headers.
        """
        msg = fix.Message()
        msg.getHeader().setField(fix.BeginString(context.session_BeginString[sessionID.toString()]))
        msg.getHeader().setField(fix.MsgType(fix.MsgType_Logon))
        msg.getHeader().setField(fix.MsgSeqNum(1))

        msg.getHeader().setField(fix.SenderCompID(
            context.session_settings[sessionID.toString()].getString('SenderCompID')
        ))
        msg.getHeader().setField(fix.TargetCompID(
            context.session_settings[sessionID.toString()].getString('TargetCompID')
        ))

        # Set TargetSubID if present in config (not done automatically for some reason)
        try:
            TargetSubID = context.session_settings[sessionID.toString()].getString('TargetSubID')
            msg.getHeader().setField(fix.TargetSubID(TargetSubID))
        except fix.ConfigError as e:
            pass

        # Set SenderLocationID if present (not done automatically for some reason)
        try:
            SenderLocationID = context.session_settings[sessionID.toString()].getString('SenderLocationID')
            msg.getHeader().setField(fix.SenderLocationID(SenderLocationID))
        except fix.ConfigError as e:
            pass

        msg.getHeader().setField(fix.SendingTime())

        return msg

    @staticmethod
    def LogonMessage(context, sessionID):
        """
        Creates a Logon (A) FIX message.
        ref: https://www.onixs.biz/fix-dictionary/4.3/msgtype_a_65.html

        Args:
            context (object): The application context containing session details and credentials.
            sessionID (object): The session ID for the FIX connection.

        Returns:
            fix.Message: A FIX logon message.
        """
        msg = MessageCreator.gen_new_message(context, sessionID=sessionID)
        msg.setField(fix.EncryptMethod(fix.EncryptMethod_NONE)) #0
        msg.setField(fix.HeartBtInt(30))
        msg.setField(fix.ResetSeqNumFlag(True))
        if context.username: msg.setField(fix.Username(context.username))
        if context.password: msg.setField(fix.Password(context.password))
        if context.newpassword: msg.setField(fix.NewPassword(context.newpassword))

        # DEPRECATED: These are now added by the Base FIX application when processing LOGON messages
        # DEPRECATED: Kept here as a reminder in case other scenatios arise where fields need adding

        # Set defaultApplExtID
        #msg.setField(fix.DefaultApplExtID(100))

        # Set NextExpectedMsgSeqNum
        #msg.setField(fix.NextExpectedMsgSeqNum(8))

        # Set DefaultApplVerID
        #msg.setField(fix.DefaultApplVerID("9"))

        return msg

    @staticmethod
    def TestRequest(context, sessionID):
        """
        Creates a TestRequest (1) FIX message.
        ref: https://www.onixs.biz/fix-dictionary/4.0/msgtype_1_1.html

        Args:
            context (object): The application context containing session details.
            sessionID (object): The session ID for the FIX connection.

        Returns:
            fix.Message: A FIX test request message.
        """
        msg = MessageCreator.gen_new_message(context, sessionID=sessionID)
        msg.getHeader().setField(fix.MsgType(fix.MsgType_TestRequest))
        msg.setField(fix.TestReqID(context._gen_TestReqID()))

        return msg

    @staticmethod
    def NewOrderSingle(context, sessionID, symbol, qty, price, side):
        """
        Creates a NewOrderSingle (D) FIX message.
        ref: https://www.onixs.biz/fix-dictionary/4.4/msgtype_d_68.html

        Args:
            context (object): The application context containing session details.
            sessionID (object): The session ID for the FIX connection.
            symbol (str): The symbol for the financial instrument (e.g., "AAPL").
            qty (float): The quantity of the order.
            price (float): The price per unit of the order.
            side (str): The side of the order (e.g., fix.Side_BUY).

        Returns:
            fix.Message: A FIX new order single message.
        """
        msg = MessageCreator.gen_new_message(context, sessionID=sessionID)
        msg.getHeader().setField(fix.MsgType(fix.MsgType_NewOrderSingle))

        #msg.setField(fix.SecurityType(fix.SecurityType_FOREIGN_EXCHANGE_CONTRACT))
        msg.setField(fix.ClOrdID(context._gen_ClOrdID()))
        msg.setField(fix.OrdType(fix.OrdType_LIMIT))
        msg.setField(fix.Side(side))
        msg.setField(fix.Symbol(symbol))
        msg.setField(fix.OrderQty(qty))
        msg.setField(fix.Price(price))
        msg.setField(fix.TimeInForce(fix.TimeInForce_GOOD_TILL_CANCEL))
        msg.setField(fix.HandlInst(fix.HandlInst_AUTOMATED_EXECUTION_ORDER_PRIVATE_NO_BROKER_INTERVENTION))
        msg.setField(fix.TransactTime())

        return msg

    @staticmethod
    def OrderCancelRequest(context, sessionID, orderHID, text="Cancel my order!"):
        """
        Creates an OrderCancelRequest (F) FIX message.

        Args:
            context (object): The application context containing session details.
            sessionID (object): The session ID for the FIX connection.
            orderHID (str): The unique order history ID.
            text (str): The message for the order. Defaults to "Cancel my order!"

        Returns:
            fix.Message: A FIX order cancel request message.
        """
        try:
            session_num = context._get_session_num(sessionID)
            msg = context.str_to_msg(context.get_session_message_log(session_num)[int(orderHID)]["msg"])
            msg.getHeader().setField(fix.MsgType(fix.MsgType_OrderCancelRequest))

            # Get values from original order message
            ClOrdID = context._gen_ClOrdID()
            OrigClOrdID = msg.getField(fix.ClOrdID().getField())
            OrderQty = msg.getField(fix.OrderQty().getField())
            Side = msg.getField(fix.Side().getField())
            Symbol = msg.getField(fix.Symbol().getField())

            # Remove unnecessary fields
            msg.removeField(fix.HandlInst().getField()) # 21
            msg.removeField(fix.OrdType().getField()) #40
            msg.removeField(fix.Price().getField()) # 44
            msg.removeField(fix.TimeInForce().getField()) # 59

            # Set appropriate fields
            msg.setField(fix.ClOrdID(ClOrdID))
            msg.setField(fix.OrigClOrdID(OrigClOrdID))
            msg.setField(fix.OrderQty(float(OrderQty)))
            msg.setField(fix.Side(Side))
            msg.setField(fix.Symbol(Symbol))
            msg.setField(fix.Text(text))
            msg.setField(fix.TransactTime())

            return msg

        except (ValueError, FieldNotFound):
            raise InvalidArgsError()

    @staticmethod
    def OrderStatusRequest(context, sessionID, orderHID):
        """
        Creates a new OrderStatusRequest (H) message
        ref: https://www.onixs.biz/fix-dictionary/4.4/msgtype_h_72.html

        Args:
            context (object): The application context containing session details.
            sessionID (object): The session ID for the FIX connection.
            orderHID (str): The unique order history ID.

        Returns:
            fix.Message: A FIX order status request message.
        """
        try:
            session_num = context._get_session_num(sessionID)
            msg = context.str_to_msg(context.get_session_message_log(session_num)[int(orderHID)]["msg"])
            msg.getHeader().setField(fix.MsgType(fix.MsgType_OrderStatusRequest))

            # Get values from original order message
            ClOrdID = context._gen_ClOrdID()
            OrigClOrdID = msg.getField(fix.ClOrdID().getField())
            Side = msg.getField(fix.Side().getField())
            Symbol = msg.getField(fix.Symbol().getField())

            #  Remove unnecessary fields
            msg.removeField(fix.HandlInst().getField()) # 21
            msg.removeField(fix.OrderQty().getField()) # 38
            msg.removeField(fix.OrdType().getField()) # 40
            msg.removeField(fix.Price().getField()) # 44
            msg.removeField(fix.TimeInForce().getField()) # 59
            msg.removeField(fix.TransactTime().getField()) # 60

            # Set appropriate fields
            msg.setField(fix.ClOrdID(ClOrdID))
            msg.setField(fix.OrigClOrdID(OrigClOrdID))
            msg.setField(fix.Side(Side))
            msg.setField(fix.Symbol(Symbol))

            return msg

        except (ValueError, FieldNotFound):
            raise InvalidArgsError()

    @staticmethod
    def QuoteRequest(context, sessionID, symbol, qty, price, side):
        """
        Creates a new QuoteRequest (R) message
        ref: https://www.onixs.biz/fix-dictionary/4.4/msgtype_r_82.html

        Args:
            context (object): The application context containing session details.
            sessionID (object): The session ID for the FIX connection.
            symbol (str): The symbol for the financial instrument (e.g., "AAPL").
            qty (float): The quantity of the order.
            price (float): The price per unit of the order.
            side (str): The side of the order (e.g., fix.Side_BUY).

        Returns:
            fix.Message: A FIX order quote request message.
        """
        msg = MessageCreator.gen_new_message(context, sessionID=sessionID)
        msg.getHeader().setField(fix.MsgType(fix.MsgType_QuoteRequest))

        msg.setField(fix.ClOrdID(context._gen_QuoteReqID()))
        msg.setField(fix.ClOrdID(context._gen_ClOrdID()))
        msg.setField(fix.Side(side))
        msg.setField(fix.SecurityType(fix.SecurityType_FOREIGN_EXCHANGE_CONTRACT))
        msg.setField(fix.HandlInst(fix.HandlInst_AUTOMATED_EXECUTION_ORDER_PRIVATE_NO_BROKER_INTERVENTION))
        msg.setField(fix.TimeInForce(fix.TimeInForce_GOOD_TILL_CANCEL))
        msg.setField(fix.Symbol(symbol))
        msg.setField(fix.OrdType(fix.OrdType_LIMIT))
        msg.setField(fix.OrderQty(qty))
        msg.setField(fix.Price(price))
        msg.setField(fix.TransactTime())

        return msg

    @staticmethod
    def MarketDataRequest(context, sessionID, sub_type, depth, update_type, symbol):
        """
        Creates a MarketDataRequest (V) FIX message.
        ef: https://www.onixs.biz/fix-dictionary/4.4/msgtype_v_86.html

        Args:
            context (object): The application context containing session details.
            sessionID (object): The session ID for the FIX connection.
            sub_type (str): Subscription request type (e.g., fix.SubscriptionRequestType_SNAPSHOT).
            depth (int): Market depth (e.g., 1 for top-of-book).
            update_type (int): Update type for market data.
            symbol (str): The symbol for the financial instrument.

        Returns:
            fix.Message: A FIX market data request message.
        """
        msg = MessageCreator.gen_new_message(context, sessionID=sessionID)
        msg.getHeader().setField(fix.MsgType(fix.MsgType_MarketDataRequest))

        msg.setField(fix.MDReqID(context._gen_MDReqID()))
        msg.setField(fix.SubscriptionRequestType(sub_type))
        msg.setField(fix.MarketDepth(depth))
        msg.setField(fix.MDUpdateType(update_type))

        # Outline 2 MDEntries are to follow
        msg.setField(fix.NoMDEntryTypes(2))
        group = fix44.MarketDataRequest().NoMDEntryTypes()

        # Set first
        group.setField(fix.MDEntryType(fix.MDEntryType_BID))
        msg.addGroup(group)

        # Set Second
        group.setField(fix.MDEntryType(fix.MDEntryType_OFFER))
        msg.addGroup(group)

        # Outline the related symbols
        msg.setField(fix.NoRelatedSym(1))
        symb = fix44.MarketDataRequest().NoRelatedSym()
        symb.setField(fix.Symbol(symbol))
        msg.addGroup(symb)

        return msg
