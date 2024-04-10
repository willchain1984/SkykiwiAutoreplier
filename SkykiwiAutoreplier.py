# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version 4.1.0-0-g733bf3d)
## http://www.wxformbuilder.org/
##
## PLEASE DO *NOT* EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc
import wx.adv
import poster
import pickle
import logging
import datetime
import re
import threading
from os import listdir
from urllib.parse import urlparse, urlsplit, parse_qsl
from aichat import call_with_messages

HOST_NAME = "bbs.skykiwi.com"
LOGIN_URL = "https://passport.skykiwi.com/v1/login/bbslogon.do"
MSG_MAX = 30
TIMER_INTVAL = 60

logging.basicConfig(
    level=logging.INFO,
    filename="info.log",
    format="%(asctime)s %(filename)s %(funcName)s：line %(lineno)d %(levelname)s %(message)s",
)

###########################################################################
## Class MyFrame1
###########################################################################


class MyFrame(wx.Frame):
    counter = 0

    def __init__(self, parent):
        wx.Frame.__init__(
            self,
            parent,
            id=wx.ID_ANY,
            title="Skykiwi AutoReplier",
            pos=wx.DefaultPosition,
            size=wx.Size(600, 420),
            style=wx.CAPTION
            | wx.CLOSE_BOX
            | wx.MINIMIZE
            | wx.MINIMIZE_BOX
            | wx.TAB_TRAVERSAL,
        )

        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)
        self.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_3DLIGHT))

        bSizer1 = wx.BoxSizer(wx.VERTICAL)

        sbSizer2 = wx.StaticBoxSizer(
            wx.StaticBox(self, wx.ID_ANY, "Skykiwi Account Info:"), wx.HORIZONTAL
        )
        self.m_staticText1 = wx.StaticText(
            sbSizer2.GetStaticBox(),
            wx.ID_ANY,
            "User：",
            wx.DefaultPosition,
            wx.DefaultSize,
            0,
        )
        self.m_staticText1.Wrap(-1)

        sbSizer2.Add(self.m_staticText1, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        context_name = "CONTEXT.DATA"
        history_name = "HISTORY"
        if context_name in listdir():
            try:
                with open(context_name, "rb") as f:
                    ctx = pickle.load(f)
                self.credential = ctx["credential"]
                self.messages = ctx["messages"]
            except Exception:
                logging.warning("Failed to read the saved context.")

        if history_name in listdir():
            try:
                with open(history_name, "rb") as f:
                    ctx = pickle.load(f)
                self.history = ctx
            except Exception:
                logging.warning("Failed to read from the saved history.")

        txt_user = self.credential["username"] if hasattr(self, "credential") else ""
        txt_pass = self.credential["password"] if hasattr(self, "credential") else ""
        self.m_user = wx.TextCtrl(
            sbSizer2.GetStaticBox(),
            wx.ID_ANY,
            txt_user,
            wx.DefaultPosition,
            wx.DefaultSize,
            0,
        )
        sbSizer2.Add(self.m_user, 1, wx.ALL, 5)
        self.m_staticText2 = wx.StaticText(
            sbSizer2.GetStaticBox(),
            wx.ID_ANY,
            "Pass:",
            wx.DefaultPosition,
            wx.DefaultSize,
            0,
        )
        self.m_staticText2.Wrap(-1)

        sbSizer2.Add(self.m_staticText2, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.m_pass = wx.TextCtrl(
            sbSizer2.GetStaticBox(),
            wx.ID_ANY,
            txt_pass,
            wx.DefaultPosition,
            wx.DefaultSize,
            wx.TE_PASSWORD,
        )
        sbSizer2.Add(self.m_pass, 1, wx.ALL, 5)

        self.m_bt_login = wx.Button(
            sbSizer2.GetStaticBox(),
            wx.ID_ANY,
            "Login",
            wx.DefaultPosition,
            wx.DefaultSize,
            0,
        )
        sbSizer2.Add(self.m_bt_login, 1, wx.ALL | wx.EXPAND, 5)
        self.m_bt_start = wx.Button(
            sbSizer2.GetStaticBox(),
            wx.ID_ANY,
            "Start Schedule",
            wx.DefaultPosition,
            wx.DefaultSize,
            0,
        )
        self.m_bt_start.Enable(False)
        sbSizer2.Add(self.m_bt_start, 1, wx.ALL | wx.EXPAND, 5)

        bSizer1.Add(sbSizer2, 0, wx.EXPAND | wx.ALL, 5)

        bSizer3 = wx.BoxSizer(wx.VERTICAL)

        self.m_panel1 = wx.Panel(
            self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL
        )
        sbSizer1 = wx.StaticBoxSizer(
            wx.StaticBox(self.m_panel1, wx.ID_ANY, "Reply Settings:"), wx.HORIZONTAL
        )

        bSizer4 = wx.BoxSizer(wx.VERTICAL)

        bSizer6 = wx.BoxSizer(wx.HORIZONTAL)

        self.m_staticText4 = wx.StaticText(
            sbSizer1.GetStaticBox(),
            wx.ID_ANY,
            "Reply ID:",
            wx.DefaultPosition,
            wx.DefaultSize,
            0,
        )
        self.m_staticText4.Wrap(-1)

        bSizer4.Add(self.m_staticText4, 0, wx.EXPAND | wx.RIGHT | wx.LEFT, 5)

        self.m_cbox_replyid = wx.adv.BitmapComboBox(
            sbSizer1.GetStaticBox(),
            wx.ID_ANY,
            "Please input a post URL or select one from the list...",
            wx.DefaultPosition,
            wx.Size(80, -1),
            [],
            0,
        )
        bSizer4.Add(
            self.m_cbox_replyid, 0, wx.EXPAND | wx.BOTTOM | wx.RIGHT | wx.LEFT, 5
        )

        self.m_staticText6 = wx.StaticText(
            sbSizer1.GetStaticBox(),
            wx.ID_ANY,
            "Reply Content:",
            wx.DefaultPosition,
            wx.DefaultSize,
            0,
        )
        self.m_staticText6.Wrap(-1)

        bSizer4.Add(self.m_staticText6, 0, wx.RIGHT | wx.LEFT, 5)

        if hasattr(self, "messages"):
            m_cbox_replymsgChoices = self.messages
        else:
            m_cbox_replymsgChoices = [
                "[AI][RE:TITLE]",
                "[AI][AUTO]",
                "膜拜神贴，后面的请保持队形~",
                "啥也不说了，楼主就是给力！",
                "果断MARK，前十有我必火！",
                "看了LZ的帖子，我只想说一句很好很强大！",
                "不错，又占了一个沙发！",
                "哥顶的不是帖子，是寂寞！",
                "果断回帖，如果沉了就是我弄沉的很有成就感",
                "找了很久，终于找到了~",
                "这个真的很好很不错，我很喜欢~",
                "我回帖不是为了赞同，只是为了让楼主的帖子看起来不那么孤单。",
                "别人在帖子里找到答案，我在帖子里找到了存在感。",
                "我回帖就像小黄鸭，虽然不起眼，但总能给帖子增添一些乐趣。",
                "回帖如同投资，有时候投入的越多，收获的可能性也就越大。",
                "我回帖的速度，比互联网还快，因为我是互联网上的“飞快手”们。",
                "别人回帖像跑步，一气呵成，我回帖像慢跑，慢慢来，但能坚持得更久。",
                "我回帖就像打太极，看似轻松，实则经过一番内心挣扎。",
                "我回帖不是在水帖，只是在为帖子增添一些生机。",
                "回帖就像扔石子进湖里，一波又一波，最终形成了美丽的涟漪。",
                "我回帖，不是为了被点赞，只是想让楼主知道，他并不孤单。",
                "我回帖的速度，比韩寒写小说还快，毕竟灵感来了就得赶紧抓住。",
                "回帖就像是下棋，要考虑每一步的走向，以免被对手困扰。",
                "我回帖就像拧瓶盖，有时候要费点劲，但总能打开话匣子。",
                "回帖如同泡茶，要慢慢品味，才能感受到其中的韵味。",
                "我回帖就像是给楼主打气，让他继续坚持下去。",
                "回帖就像煮面，要掌握好火候，才能做出美味可口的回复。",
                "回帖如同划船，用力过猛会掀起浪花，用力过轻会停滞不前。",
                "我回帖的速度，比火箭还快，因为我是火箭帖。",
                "回帖如同种花，不断浇灌，才能看到绚烂的花开。",
                "我回帖就像撩妹，要用心灵手巧，才能引起共鸣。",
            ]
        self.m_cbox_replymsg = wx.ComboBox(
            sbSizer1.GetStaticBox(),
            wx.ID_ANY,
            "Please input reply content here...",
            wx.DefaultPosition,
            wx.Size(250, -1),
            m_cbox_replymsgChoices,
            0,
        )
        bSizer4.Add(
            self.m_cbox_replymsg, 1, wx.EXPAND | wx.BOTTOM | wx.RIGHT | wx.LEFT, 5
        )

        self.m_staticText5 = wx.StaticText(
            sbSizer1.GetStaticBox(),
            wx.ID_ANY,
            "Interval:",
            wx.DefaultPosition,
            wx.DefaultSize,
            0,
        )
        self.m_staticText5.Wrap(-1)
        bSizer6.Add(self.m_staticText5, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        self.m_slider_intval = wx.Slider(
            sbSizer1.GetStaticBox(),
            wx.ID_ANY,
            360,
            5,
            60 * 24 * 7,
            wx.DefaultPosition,
            wx.Size(80, -1),
            wx.SL_HORIZONTAL,
        )
        bSizer6.Add(self.m_slider_intval, 0, wx.ALL, 5)

        self.m_txtInt = wx.StaticText(
            sbSizer1.GetStaticBox(),
            wx.ID_ANY,
            str(self.m_slider_intval.Value) + " Mins",
            wx.DefaultPosition,
            wx.DefaultSize,
            0,
        )
        self.m_txtInt.Wrap(-1)
        bSizer6.Add(self.m_txtInt, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        self.m_bt_add = wx.Button(
            sbSizer1.GetStaticBox(),
            wx.ID_ANY,
            "Schedule ->",
            wx.DefaultPosition,
            wx.Size(-1, -1),
            0,
        )
        bSizer6.Add(self.m_bt_add, 1, wx.ALL | wx.EXPAND, 5)

        bSizer4.Add(bSizer6, 0, 0, 5)

        self.m_bt_reply = wx.Button(
            sbSizer1.GetStaticBox(),
            wx.ID_ANY,
            "Reply Once",
            wx.DefaultPosition,
            wx.DefaultSize,
            0,
        )
        bSizer4.Add(self.m_bt_reply, 1, wx.RIGHT | wx.EXPAND, 5)

        sbSizer1.Add(bSizer4, 0, 0, 5)

        bSizer5 = wx.BoxSizer(wx.VERTICAL)

        m_lbox_tidlistChoices = []
        self.m_lbox_tidlist = wx.ListBox(
            sbSizer1.GetStaticBox(),
            wx.ID_ANY,
            wx.DefaultPosition,
            wx.Size(-1, 127),
            m_lbox_tidlistChoices,
            wx.LB_HSCROLL,
        )
        bSizer5.Add(self.m_lbox_tidlist, 1, wx.BOTTOM | wx.EXPAND, 5)

        bSizer7 = wx.BoxSizer(wx.HORIZONTAL)

        bSizer7.Add((0, 0), 1, wx.EXPAND, 5)
        self.m_bt_exec = wx.Button(
            sbSizer1.GetStaticBox(),
            wx.ID_ANY,
            "Exec",
            wx.DefaultPosition,
            wx.Size(40, 30),
            0,
        )
        self.m_bt_exec.Enable(False)
        bSizer7.Add(self.m_bt_exec, 1, 0, 5)

        self.m_button_del = wx.Button(
            sbSizer1.GetStaticBox(),
            wx.ID_ANY,
            "Del",
            wx.DefaultPosition,
            wx.Size(40, 30),
            0,
        )
        bSizer7.Add(self.m_button_del, 1, 0, 5)

        bSizer5.Add(bSizer7, 1, wx.EXPAND, 5)
        sbSizer1.Add(bSizer5, 1, wx.EXPAND, 5)

        self.m_panel1.SetSizer(sbSizer1)
        self.m_panel1.Layout()
        sbSizer1.Fit(self.m_panel1)
        bSizer3.Add(self.m_panel1, 1, wx.EXPAND | wx.ALL, 5)
        bSizer1.Add(bSizer3, 1, wx.EXPAND, 5)

        bSizerlog = wx.StaticBoxSizer(
            wx.StaticBox(self, wx.ID_ANY, "History Info:"), wx.HORIZONTAL
        )

        self.m_log = wx.TextCtrl(
            self,
            wx.ID_ANY,
            wx.EmptyString,
            wx.DefaultPosition,
            wx.Size(-1, 56),
            wx.TE_MULTILINE | wx.TE_READONLY,
        )
        self.m_log.SetFont(
            wx.Font(
                9,
                wx.FONTFAMILY_DEFAULT,
                wx.FONTSTYLE_NORMAL,
                wx.FONTWEIGHT_NORMAL,
                False,
                "宋体",
            )
        )
        bSizerlog.Add(self.m_log, 1, wx.ALL | wx.EXPAND, 5)

        bSizerlogbt = wx.BoxSizer(wx.VERTICAL)
        self.m_bt_save = wx.Button(
            self, wx.ID_ANY, "Save", wx.DefaultPosition, wx.Size(40, -1), 0
        )
        bSizerlogbt.Add(self.m_bt_save, 1, wx.TOP, 5)
        self.m_bt_clear = wx.Button(
            self, wx.ID_ANY, "Clear", wx.DefaultPosition, wx.Size(40, -1), 0
        )
        bSizerlogbt.Add(self.m_bt_clear, 1, wx.BOTTOM, 5)
        bSizerlog.Add(bSizerlogbt, 0, wx.EXPAND, 5)

        bSizer1.Add(bSizerlog, 0, wx.RIGHT | wx.EXPAND, 5)

        self.SetSizer(bSizer1)
        self.Layout()
        self.m_statusBar = self.CreateStatusBar(
            1, wx.STB_SIZEGRIP | wx.ALIGN_RIGHT, wx.ID_ANY
        )
        self.m_statusBar.SetFieldsCount(2)
        self.m_statusBar.SetStatusWidths([-3, -1])
        self.m_statusBar.SetStatusText("Auto-running stopped.".rjust(26), 1)

        self.m_panel1.Enable(False)

        self.Centre(wx.BOTH)

        # Connect Events
        self.Bind(wx.EVT_CLOSE, self.MyFrameOnClose)
        self.m_bt_login.Bind(wx.EVT_BUTTON, self.m_bt_loginOnButtonClick)
        self.m_bt_reply.Bind(wx.EVT_BUTTON, self.m_bt_replyOnButtonClick)
        self.m_bt_add.Bind(wx.EVT_BUTTON, self.m_bt_addOnButtonClick)
        self.m_bt_exec.Bind(wx.EVT_BUTTON, self.m_bt_execOnButtonClick)
        self.m_button_del.Bind(wx.EVT_BUTTON, self.m_button_delOnButtonClick)
        self.m_bt_start.Bind(wx.EVT_BUTTON, self.m_bt_startOnButtonClick)
        self.m_bt_clear.Bind(wx.EVT_BUTTON, self.m_bt_clearOnButtonClick)
        self.m_bt_save.Bind(wx.EVT_BUTTON, self.m_bt_saveOnButtonClick)
        self.m_slider_intval.Bind(
            wx.EVT_SCROLL_CHANGED, self.m_slider_intvalOnScrollChanged
        )
        self.m_lbox_tidlist.Bind(wx.EVT_LISTBOX, self.m_lbox_tidlistOnListBox)
        self.m_lbox_tidlist.Bind(wx.EVT_UPDATE_UI, self.m_lbox_tidlistOnUpdateUI)

        self.tasks = {}
        self.IsLogin = False
        self.IsFirstLogin = True
        self.timer = wx.Timer(self)
        self.status_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self._timer_scan, self.timer)
        self.Bind(wx.EVT_TIMER, self._update_status, self.status_timer)

    def __del__(self):
        pass

    # Virtual event handlers, override them in your derived class
    def MyFrameOnClose(self, event):
        if self.timer.IsRunning():
            self.timer.Stop()
            self.status_timer.Stop()
        history = self.m_log.Value
        try:
            with open("HISTORY", "wb") as f:
                pickle.dump(history, f)
                logging.info("Successed to save the history info when exit..")
        except Exception:
            logging.warning("Failed to save the history info when exit.")

        if hasattr(self, "credential") and (not self.IsFirstLogin):
            context = {
                "credential": self.credential,
                "tasks": self.tasks,
                "messages": self.m_cbox_replymsg.GetItems()[0:MSG_MAX],
            }
            context_name = "CONTEXT.DATA"
            try:
                with open(context_name, "wb") as f:
                    pickle.dump(context, f)
                    logging.info("Successed to save the context when exit.")
                    self.is_context_saved = True
            except Exception:
                logging.warning("Failed to save the context when exit.")
        # self.Destroy()
        self.Hide()
        event.Skip()

    def m_bt_loginOnButtonClick(self, event):
        threading.Thread(target=self._async_login, daemon=True).start()
        event.Skip()

    def m_bt_replyOnButtonClick(self, event):
        if (
            not self.m_cbox_replyid.Value
            == "Please input a post URL or select one from the list..."
        ):
            replyid = self.m_cbox_replyid.Value
            title = ""
            if (
                len(replyid.split("|")) > 0
                and replyid.split("|")[0].strip().isnumeric()
            ):
                tid = replyid.split("|")[0].strip()
                title = replyid.split("|")[1].strip()
                # print(tid)
            elif replyid.isnumeric():
                tid = replyid
            elif re.match(
                f"http://{HOST_NAME}/forum\.php\?mod=viewthread[\S+]", replyid
            ):
                dt = dict(parse_qsl(urlsplit(replyid).query))
                if "tid" in dt.keys():
                    tid = dt["tid"]
                else:
                    wx.MessageBox(
                        "Invalid post URL or TID provided, please check and retry!",
                        "Info",
                        wx.OK | wx.ICON_INFORMATION,
                    )
                    return False
            else:
                wx.MessageBox(
                    "Invalid post URL or TID provided, please check and retry!",
                    "Info",
                    wx.OK | wx.ICON_INFORMATION,
                )
                return False
            message = self.m_cbox_replymsg.Value
            self.update_msg_list(message)
            threading.Thread(
                target=self._async_reply,
                args=(
                    message,
                    tid,
                    title,
                ),
                daemon=True,
            ).start()
        event.Skip()

    def m_bt_addOnButtonClick(self, event):
        if (
            not self.m_cbox_replyid.Value
            == "Please input a post URL or select one from the list..."
        ):
            replyid = self.m_cbox_replyid.Value
            if (
                len(replyid.split("|")) > 0
                and replyid.split("|")[0].strip().isnumeric()
            ):
                tid = replyid.split("|")[0].strip()
                title = replyid.split("|")[1].strip()
            elif replyid.isnumeric():
                tid = replyid
                title = self.discuz.get_title_by_tid(tid)
            elif re.match(
                f"http://{HOST_NAME}/forum\.php\?mod=viewthread[\S+]", replyid
            ):
                dt = dict(parse_qsl(urlsplit(replyid).query))
                if "tid" in dt.keys():
                    tid = dt["tid"]
                    title = self.discuz.get_title_by_tid(tid)
                else:
                    wx.MessageBox(
                        "Please check the URL provided!",
                        "Info",
                        wx.OK | wx.ICON_INFORMATION,
                    )
                    return False
            else:
                wx.MessageBox(
                    "Please check the Reply ID info provided!",
                    "Info",
                    wx.OK | wx.ICON_INFORMATION,
                )
                return False
            for item in self.m_lbox_tidlist.GetStrings():
                if tid == item.split("|")[0].strip():
                    wx.MessageBox(
                        "Repeated TID found in the list",
                        "Info",
                        wx.OK | wx.ICON_INFORMATION,
                    )
                    return False
            message = self.m_cbox_replymsg.Value
            self.update_msg_list(message)
            intval = self.m_slider_intval.Value
            taskitem = {
                "interval": intval,
                "title": title,
                "message": message,
                "countdown": intval * 60,
            }
            self.tasks[tid] = taskitem
            # print (self.tasks)
            self.m_cbox_replyid.SetValue(f"{tid} | {title}")
            self.m_lbox_tidlist.Append(f"{tid} | {intval} | {title} | {message}")
        event.Skip()

    def m_bt_execOnButtonClick(self, event):
        index = self.m_lbox_tidlist.GetSelection()
        args = self.m_lbox_tidlist.GetString(index).split(" | ")
        if len(args) > 0:
            tid = args[0]
            message = self.tasks[tid]["message"]
            title = self.tasks[tid]["title"]
            self.m_cbox_replyid.SetValue(f"{tid} | {title}")
            self.m_cbox_replymsg.SetValue(message)
            evt = wx.CommandEvent(wx.EVT_BUTTON.typeId, self.m_bt_reply.GetId())
            evt.SetEventObject(self.m_bt_reply)
            # print("bingo!")
            self.m_bt_reply.ProcessEvent(evt)
        event.Skip()

    def m_button_delOnButtonClick(self, event):
        index = self.m_lbox_tidlist.GetSelection()
        if index > -1:
            tid = self.m_lbox_tidlist.GetString(index).split("|")[0].strip()
            self.m_lbox_tidlist.Delete(index)
            del self.tasks[tid]
            # print(self.tasks)
        event.Skip()

    def m_bt_startOnButtonClick(self, event):
        if self.timer.IsRunning():
            self.timer.Stop()
            self.status_timer.Stop()
            self.m_panel1.Enable(True)
            self.m_bt_start.SetLabel("Start Schedule")
            self.m_statusBar.SetStatusText("Auto-running stopped.".rjust(26), 1)

        else:
            if len(self.tasks):
                self.timer.Start(1000 * TIMER_INTVAL)
                self.status_timer.Start(200)
                self.m_bt_start.SetLabel("Stop Running")
            else:
                wx.MessageBox(
                    "No task has been added to the schedule!",
                    "Info",
                    wx.OK | wx.ICON_INFORMATION,
                )
        event.Skip()

    def m_slider_intvalOnScrollChanged(self, event):
        self.m_txtInt.SetLabel(f"{self.m_slider_intval.Value} Mins")
        event.Skip()

    def m_lbox_tidlistOnListBox(self, event):
        if self.m_lbox_tidlist.GetSelection() > -1:
            self.m_bt_exec.Enable(True)
        else:
            self.m_bt_exec.Enable(False)
        event.Skip()

    def m_bt_clearOnButtonClick(self, event):
        ret = wx.MessageBox(
            "Are you sure to clear all the recorded actions?",
            "Info",
            wx.YES | wx.NO | wx.ICON_INFORMATION,
        )
        if ret == wx.YES:
            self.m_log.Clear()
            self.history = None
        event.Skip()

    def m_bt_saveOnButtonClick(self, event):
        filename = f"history_{datetime.datetime.now().strftime('%Y%m%d%H%M')}.txt"
        with wx.FileDialog(
            self,
            "Save history file",
            defaultFile=filename,
            wildcard="txt files (*.txt)|*.txt",
            style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT,
        ) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return
            pathname = fileDialog.GetPath()
            try:
                with open(pathname, "w") as file:
                    file.writelines(self.m_log.Value)
            except IOError:
                logging.error(
                    "An error occured when export the history info to the path: '%s'"
                    % pathname
                )
        event.Skip()

    def m_lbox_tidlistOnUpdateUI(self, event):
        if self.m_lbox_tidlist.GetSelection() > -1:
            self.m_bt_exec.Enable(True)
        else:
            self.m_bt_exec.Enable(False)
        event.Skip()

    def _async_login(self):
        if not self.IsLogin:
            user = self.m_user.Value
            passwd = self.m_pass.Value
            self.m_bt_login.Enable(False)
            self.discuz = poster.Discuz(LOGIN_URL, HOST_NAME, user, passwd)
            ret = self.discuz.login()
            if ret:
                self.IsLogin = True
                self.credential = {"username": user, "password": passwd}
                tids = self.discuz.get_myreply_tid_list()
                tids.extend(self.discuz.get_reply_tid_list())
                self.m_cbox_replyid.Clear()
                self.m_cbox_replyid.SetItems(tids)
                self.m_cbox_replyid.SetValue(
                    "Please input a post URL or select one from the list..."
                )
                self.m_panel1.Enable(True)
                self.m_user.Enable(False)
                self.m_pass.Enable(False)
                self.m_bt_start.Enable(True)
                self.m_bt_login.SetLabel("Logout")

                if self.IsFirstLogin:
                    self.IsFirstLogin = False
                    context_name = "CONTEXT.DATA"
                    if context_name in listdir():
                        try:
                            with open(context_name, "rb") as f:
                                self.tasks = pickle.load(f)["tasks"]
                        except Exception:
                            logging.warning("Failed to obtain the saved context.")
                        items = []
                        for task in self.tasks:
                            items.append(
                                f"{task} | {self.tasks[task]['interval']} | {self.tasks[task]['title']} | {self.tasks[task]['message']}"
                            )
                        if len(items):
                            self.m_lbox_tidlist.InsertItems(items, 0)

                time = datetime.datetime.now()
                timestr = time.strftime("%d/%m/%Y %H:%M:%S:")
                self.m_log.AppendText(f"#{timestr} User:{user}， Login successed!\n")

                wx.MessageBox("Login successed!", "Info", wx.OK | wx.ICON_INFORMATION)
                self.m_slider_intval.Enable(True)
            else:
                time = datetime.datetime.now()
                timestr = time.strftime("%d/%m/%Y %H:%M:%S:")
                self.m_log.AppendText(f"#{timestr} User:{user}， Login failed!\n")

                if ret == False:
                    msg = "Login failed! Please check your username and password."
                elif ret == -1:
                    msg = "Login failed due to connection error! Please check your network configuration."
                else:
                    msg = "Login failed due to an exception! Please try again."
                wx.MessageBox(
                    msg,
                    "Info",
                    wx.OK | wx.ICON_INFORMATION,
                )
            self.m_bt_login.Enable(True)

        else:
            if self.timer.IsRunning():
                evt = wx.CommandEvent(wx.EVT_BUTTON.typeId, self.m_bt_start.GetId())
                evt.SetEventObject(self.m_bt_start)
                self.m_bt_start.ProcessEvent(evt)
            self.m_bt_login.Enable(False)
            if self.discuz.logout():
                self.m_bt_login.SetLabel("Login")
                self.m_user.Enable(True)
                self.m_pass.Enable(True)
                self.m_panel1.Enable(False)
                self.m_bt_start.Enable(False)
                self.IsLogin = False
                time = datetime.datetime.now()
                timestr = time.strftime("%d/%m/%Y %H:%M:%S:")
                self.m_log.AppendText(
                    f"#{timestr} User:{self.m_user.Value}， Logout successed!\n"
                )
            else:
                time = datetime.datetime.now()
                timestr = time.strftime("%d/%m/%Y %H:%M:%S:")
                self.m_log.AppendText(
                    f"#{timestr} User:{self.m_user.Value}， Logout failed!\n"
                )
            self.m_bt_login.Enable(True)

    def _timer_scan(self, event):
        # print(self.tasks)
        for key in self.tasks:
            self.tasks[key]["countdown"] -= TIMER_INTVAL
            if self.tasks[key]["countdown"] <= 0:
                msg = self.tasks[key]["message"]
                threading.Thread(
                    target=self._get_ai_resp,
                    args=(
                        msg,
                        key,
                    ),
                    daemon=True,
                ).start()
                self.tasks[key]["countdown"] = self.tasks[key]["interval"] * 60

    def _update_status(self, event):
        m = MyFrame.counter % 4
        if m == 1:
            char = "｜"
        elif m == 2:
            char = "／"
        elif m == 3:
            char = "一"
        else:
            char = "＼"
        self.StatusBar.SetStatusText(f"Auto-running {char}".rjust(26), 1)
        MyFrame.counter = MyFrame.counter + 1 if MyFrame.counter < 600 else 0

    def _get_ai_resp(self, msg, key=""):
        title = self.tasks[key]["title"]
        if msg.startswith("[AI]"):
            msg = msg.replace("[AI]", "", 1)
            if msg == "[RE:TITLE]":
                cmd = f'Please comment and reply to following BBS title in Chinese. The title is "{title}".'
            elif msg == "[AUTO]":
                cmd = "Generate a popular BBS reply in Chinese."
            else:
                cmd = msg
            msg = call_with_messages(cmd)
            if not msg:
                time = datetime.datetime.now()
                timestr = time.strftime("%d/%m/%Y %H:%M:%S:")
                logtxt = f"#{timestr} User:{self.m_user.Value}, Scheduled task failed to reply, AI-API connection error!\n"
                wx.CallAfter(self._update_log, logtxt)
                return False
            else:
                msg = msg.output.choices[0].message.content
            # print(msg)
        #if True:
        if self.discuz.reply(key, msg):
            time = datetime.datetime.now()
            timestr = time.strftime("%d/%m/%Y %H:%M:%S:")
            logtxt = f"#{timestr} User:{self.m_user.Value}, Scheduled task successed to reply!\n"
            logtxt += f"Replied post:[{key}]-{title} with： "
            logtxt += f"{msg[0:80]}...\n"
        else:
            time = datetime.datetime.now()
            timestr = time.strftime("%d/%m/%Y %H:%M:%S:")
            logtxt = f"#{timestr} User:{self.m_user.Value}, Schedule task failed to reply [{key}]-{title}!\n"
        wx.CallAfter(self._update_log, logtxt)

    def _update_log(self, msg):
        self.m_log.AppendText(msg)

    def _async_reply(self, msg, key, title):
        self.m_panel1.Enable(False)
        if msg.startswith("[AI]"):
            msg = msg.replace("[AI]", "", 1)
            if msg == "[RE:TITLE]":
                title = title if title != "" else self.discuz.get_title_by_tid(key)
                cmd = f'Please comment and reply to following BBS title in Chinese. The title is "{title}".'
            elif msg == "[AUTO]":
                cmd = "Generate a popular BBS reply in Chinese."
            else:
                cmd = msg
            msg = call_with_messages(cmd)
            if not msg:
                time = datetime.datetime.now()
                timestr = time.strftime("%d/%m/%Y %H:%M:%S:")
                self.m_log.AppendText(
                    f"#{timestr} User:{self.m_user.Value}, Reply failed, AI API connection error!\n"
                )
                return False
            else:
                msg = msg.output.choices[0].message.content
            # print(message)
        if self.discuz.reply(key, msg):
            title = title if title != "" else self.discuz.get_title_by_tid(key)
            self.m_cbox_replyid.SetValue(f"{key} | {title}")
            time = datetime.datetime.now()
            timestr = time.strftime("%d/%m/%Y %H:%M:%S:")
            self.m_log.AppendText(
                f"#{timestr} User:{self.m_user.Value}, Reply successed!\n"
            )
            self.m_log.AppendText(f"Replied post:[{key}]-{title} with: ")
            self.m_log.AppendText(f"{msg[0:80]}...\n")
            wx.MessageBox("Reply successed!", "Info", wx.OK | wx.ICON_INFORMATION)
        else:
            time = datetime.datetime.now()
            timestr = time.strftime("%d/%m/%Y %H:%M:%S:")
            self.m_log.AppendText(
                f"#{timestr} User:{self.m_user.Value}, Reply failed!\n"
            )
            wx.MessageBox("Reply failed!", "Info", wx.OK | wx.ICON_INFORMATION)
        self.m_panel1.Enable(True)

    def update_msg_list(self, message):
        if len(message.strip()) > 8 and self.m_cbox_replymsg.FindString(message) == -1:
            self.m_cbox_replymsg.Insert(message, 2)


if __name__ == "__main__":
    app = wx.App()
    window = MyFrame(parent=None)
    if hasattr(window, "history"):
        window.m_log.SetValue(window.history)
        window.m_log.SetInsertionPoint(-1)
        window.m_log.ShowPosition(window.m_log.GetLastPosition())
    window.Show()
    """ 
    username = window.m_user.Value
    cookies_name = "COOKIES-" + username
    if cookies_name in listdir():
        evt = wx.CommandEvent(wx.EVT_BUTTON.typeId, window.m_bt_login.GetId())
        evt.SetEventObject(window.m_bt_login)
        window.m_bt_login.ProcessEvent(evt)
    """
    app.MainLoop()
