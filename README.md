# Description

Fixit is a CLI application designed to help communicate with FIX-based systems and applications. The purpose of this tool is to facilitate security testing and research activities when reviewing FIX systems without a client application. Fixit allows for the creation, modification, and sending of raw FIX messages.

This tool includes software developed by the QuickFIX project
(http://www.quickfixengine.org/).

# Installation / Requirements

The script requires miltiple libraries. It is advised that it be installed within a python virtual environment:
```
$ sudo apt install python3-venv
$ python3 -m venv fixit_env            
$ source fixit_env/bin/activate 
(fixit_env) $ python3 -m pip install -r requirements.txt
```

## Help

```
$ python ./initiator.py --help
usage: initiator.py [-h] [--version] [-s <DEFAULT_SESS>] [-u <USERNAME>] [-p <PASSWORD>]
                    [-n <NEW PASSWORD>] [-d <FIX_DELIM>] [-S <MESSAGE_STORE>] [-q SEQ_SEED]
                    [-x EXP_SEQ_SEED] [-f FUZZ_DELAY] [-r RESP_DELAY] [--colour]
                    [--log_heartbeat] [--verbose] [-P [PRELOAD ...]]
                    <CONFIG_FILE>

CLI Application for interfacing with a FIX Gateway

positional arguments:
  <CONFIG_FILE>         FIX initiator configuration file

options:
  -h, --help            show this help message and exit
  --version             show program's version number and exit

Session Configuration:
  -s <DEFAULT_SESS>, --session <DEFAULT_SESS>
                        The default FIX session to interact with
  -u <USERNAME>, --username <USERNAME>
                        FIX session username for authentication
  -p <PASSWORD>, --password <PASSWORD>
                        FIX session password for authentication
  -n <NEW PASSWORD>, --newpassword <NEW PASSWORD>
                        New password for FIX session

Message Handling:
  -d <FIX_DELIM>, --fix_delim <FIX_DELIM>
                        The delimiter used for FIX message fields
  -S <MESSAGE_STORE>, --store <MESSAGE_STORE>
                        Message store file, containing sample messages
  -q SEQ_SEED, --seq_seed SEQ_SEED
                        Initial value for message sequence number
  -x EXP_SEQ_SEED, --exp_seq_seed EXP_SEQ_SEED
                        Initial value for message sequence number

Fuzzing:
  -f FUZZ_DELAY, --fuzz_delay FUZZ_DELAY
                        Set the delay between fuzzing messages
  -r RESP_DELAY, --resp_delay RESP_DELAY
                        The time to wait for a FIX response

Console Output:
  --colour              enables coloured console output
  --log_heartbeat       Log heartbeat messages by default
  --verbose             Increase verbosity

Preloaded Commands:
  -P [PRELOAD ...], --preload [PRELOAD ...]
                        predefined commands to run on startup

Example usage:
  python initiator.py ./config/initiator.cfg --colour --preload \
  "message new ORD-BUY" "message edit 38=100" "message send" "exit"
```

# Example

Connect to a gateway, send a market order, and disconnect.
```
$ python3 ./initiator.py config/initiator.cfg --colour
    ___________  __ __________
   / ____/  _/ |/ //  _/_  __/
  / /_   / / |   / / /  / /
 / __/ _/ / /   |_/ /  / /
/_/   /___//_/|_/___/ /_/
                   version 0.1

[+] Interceptor Started on TCP 8080 -> 10.0.2.15:9878

[+] FIX Session created: FIX.4.2:SOMECLIENT->FIXIMULATORTRADE.

[+] Logging on to 'FIX.4.2:SOMECLIENT->FIXIMULATORTRADE'...

-> OUT(ADM): S:0 [00000] b'8=FIX.4.2|9=87|35=A|34=1|49=SOMECLIENT|52=20241206-03:02:24.297|56=FIXIMULATORTR...
<- IN (ADM): S:0 [00001] b'8=FIX.4.2|9=87|35=A|34=1|49=FIXIMULATORTRADE|52=20241206-03:02:24.303|56=SOMECLI...

[+] Successful Logon to session 'FIX.4.2:SOMECLIENT->FIXIMULATORTRADE'.

[FIX/SESS-0]> message new ORD-BUY
[+] Storing message: NEW_ORDER_D...
[+] Message saved: FIX.4.2:NEW_ORDER_D-D:1

[FIX/SESS-0/FIX.4.2:NEW_ORDER_D-D:1]> message edit 40=1 54=1 55=THQI 38=500 -44
[+] Message updated: 40=1
[+] Message updated: 54=1
[+] Message updated: 55=THQI
[+] Message updated: 38=500
[+] Message updated: 44 removed

[FIX/SESS-0/FIX.4.2:NEW_ORDER_D-D:1]> message view
8(BeginString)=FIX.4.2
9(BodyLength)=151
35(MsgType)=D
34(MsgSeqNum)=1
49(SenderCompID)=SOMECLIENT
52(SendingTime)=20241206-03:02:24
56(TargetCompID)=FIXIMULATORTRADE
11(ClOrdID)=1-1733454144.399551
21(HandlInst)=1
38(OrderQty)=500
40(OrdType)=1
54(Side)=1
55(Symbol)=THQI
59(TimeInForce)=1
60(TransactTime)=20241206-03:02:24
10(CheckSum)=086

[FIX/SESS-0/FIX.4.2:NEW_ORDER_D-D:1]> message send
[+] Sending message...
-> OUT(APP): S:0 [00002] b'8=FIX.4.2|9=148|35=D|34=2|49=SOMECLIENT|52=20241206-03:02:24.440|56=FIXIMULATORT...
<- IN (APP): S:0 [00003] b'8=FIX.4.2|9=191|35=8|34=2|49=FIXIMULATORTRADE|52=20241206-03:02:24.452|56=SOMECL...

[FIX/SESS-0/FIX.4.2:NEW_ORDER_D-D:1]> history
    ID  Route        Message
------  -----------  -----------------------------------------------------------------------------------------
     0  -> OUT(ADM)  A (LOGON) 8=FIX.4.2|9=87|35=A|34=1|49=SOMECLIENT|52=20241206-03:02:24.297|56=FIXIMULAT...
     1  <- IN (ADM)  A (LOGON) 8=FIX.4.2|9=87|35=A|34=1|49=FIXIMULATORTRADE|52=20241206-03:02:24.303|56=SOM...
     2  -> OUT(APP)  D (NEW_ORDER_D) 8=FIX.4.2|9=148|35=D|34=2|49=SOMECLIENT|52=20241206-03:02:24.440|56=FI...
     3  <- IN (APP)  8 (EXECUTION_REPORT) 8=FIX.4.2|9=191|35=8|34=2|49=FIXIMULATORTRADE|52=20241206-03:02:2...

[FIX/SESS-0/FIX.4.2:NEW_ORDER_D-D:1]> exit
[+] TERMINATING

[+] Logging out of 'FIX.4.2:SOMECLIENT->FIXIMULATORTRADE'...

-> OUT(ADM): S:0 [00006] b'8=FIX.4.2|9=69|35=5|34=4|49=SOMECLIENT|52=20241206-03:02:26.957|56=FIXIMULATORTR...
<- IN (ADM): S:0 [00007] b'8=FIX.4.2|9=69|35=5|34=4|49=FIXIMULATORTRADE|52=20241206-03:02:26.963|56=SOMECLI...

[+] Logged out of session 'FIX.4.2:SOMECLIENT->FIXIMULATORTRADE complete'.
[+] Terminating Interceptor on TCP: 8080
[+] Complete!
```


