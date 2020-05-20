#!/usr/bin/env python
# -*- coding: utf-8 -*-

import wx
import os
import time
import commands
from Androice import check_devices, take_screen_shot, MyException
import thread
import logger
import random
from PIL import Image

# log = logger.Log('./my_log.log', 'INFO', os.path.split(__file__)[1])
log = logger.Log('INFO', os.path.split(__file__)[1])


class MainFrame(wx.Frame):
    delayDefault = "2"
    seedDefault = "5000000"
    executeNumDefault = "60000000"
    log_dir = "./"
    root_dir = os.getcwd()
    default_package = ['com.mintegral.sdk.demo']
    monkey_p = ""
    logcat_p = ""
    current_phone = ''

    def __init__(self):
        wx.Frame.__init__(self, None, -1, "FastMonkey", pos=(480, 25), size=(420, 750),
                          style=wx.MINIMIZE_BOX | wx.CLOSE_BOX, name='frame_main')
        panel = wx.Panel(self, -1)

        x_pos = 10
        x_pos1 = 120
        x_pos2 = 300
        y_pos = 12
        y_delta = 40
        execute_mode = ["默认",
                        "忽略程序崩溃",
                        "忽略程序无响应",
                        "忽略安全异常",
                        "出错中断程序",
                        "本地代码导致的崩溃"
                        ]

        log_mode = ["简单", "普通", "详细"]
        execution_mode_default = execute_mode[0]

        menu_bar = wx.MenuBar()
        m_file = wx.Menu()
        m_file.Append(wx.MenuItem(m_file, 1, '&SaveLog'))
        m_file.Append(wx.MenuItem(m_file, 2, '&StopLog'))
        m_file.Append(wx.MenuItem(m_file, 3, '&Quit'))
        m_help = wx.Menu()
        menu_bar.Append(m_file, "&File")
        menu_bar.Append(m_help, '&Help')
        self.SetMenuBar(menu_bar)
        self.Bind(wx.EVT_MENU, self.save_logcat, id=1)
        self.Bind(wx.EVT_MENU, self.build_fatal_log, id=2)
        self.Bind(wx.EVT_MENU, self.on_quit, id=3)

        wx.StaticText(panel, -1, "种子数:", pos=(x_pos, y_pos))
        self.seedCtrl = wx.TextCtrl(panel, -1, "", pos=(x_pos1, y_pos))
        self.seedCtrl.Bind(wx.EVT_KILL_FOCUS, self.valid_seed)
        self.seedCtrl.SetFocus()

        self.checkBox = wx.CheckBox(panel, -1, "疲劳控制", pos=(x_pos2, y_pos))
        self.Bind(wx.EVT_CHECKBOX, self.check_box, self.checkBox)

        wx.StaticText(panel, -1, "执行次数:", pos=(x_pos, y_pos + y_delta))
        self.executeNumCtrl = wx.TextCtrl(panel, -1, "", pos=(x_pos1, y_pos + y_delta))
        self.executeNumCtrl.Bind(wx.EVT_KILL_FOCUS, self.valid_num)

        wx.StaticText(panel, -1, "延时:", pos=(x_pos, y_pos + 2 * y_delta))
        self.delayNumCtrl = wx.TextCtrl(panel, -1, "", pos=(x_pos1, y_pos + 2 * y_delta))
        self.delayNumCtrl.Bind(wx.EVT_KILL_FOCUS, self.valid_delay)

        wx.StaticText(panel, -1, "执行方式:", pos=(x_pos, y_pos + 3 * y_delta))
        self.executeModeCtrl = wx.ComboBox(panel, -1, "", (x_pos1, y_pos + 3 * y_delta), choices=execute_mode,
                                           style=wx.CB_READONLY)

        self.getButton = wx.Button(panel, -1, "获取设备", pos=(x_pos, y_pos + 4 * y_delta))
        self.Bind(wx.EVT_BUTTON, self.get_connect_devices, self.getButton)

        list_box = self.get_devices()
        list_size = list_box.__len__()
        if list_size > 2:
            list_size = 2
        self.listBox = wx.ListBox(panel, -1, (x_pos1, y_pos + 4 * y_delta), (280, 21 * list_size), list_box, wx.LB_SINGLE)
        if list_size > 0:
            self.listBox.SetSelection(0)

        self.checkListBox = wx.CheckListBox(panel, -1, (x_pos, y_pos + 5.2 * y_delta), (400, 350), [])

        y_pos_layout = y_pos + 15 * y_delta
        wx.StaticText(panel, -1, "日志输出等级:", pos=(x_pos, y_pos_layout - y_delta))
        self.logModeCtrl = wx.ComboBox(panel, -1, "", (x_pos1, y_pos_layout - y_delta), choices=log_mode,
                                       style=wx.CB_READONLY)

        self.readButton = wx.Button(panel, -1, "读取程序包", pos=(x_pos, y_pos_layout))
        self.Bind(wx.EVT_BUTTON, self.get_package_list, self.readButton)

        self.selectButton = wx.Button(panel, -1, "全部选择", pos=(x_pos + 120, y_pos_layout))
        self.Bind(wx.EVT_BUTTON, self.on_select_all, self.selectButton)

        self.unSelectButton = wx.Button(panel, -1, "全部取消", pos=(x_pos + 120 * 2, y_pos_layout))
        self.Bind(wx.EVT_BUTTON, self.on_unselect, self.unSelectButton)

        self.defaultButton = wx.Button(panel, -1, "默认参数", pos=(x_pos, y_pos_layout + y_delta))
        self.Bind(wx.EVT_BUTTON, self.on_reset, self.defaultButton)

        self.quickButton = wx.Button(panel, -1, "一键Monkey", pos=(x_pos + 120, y_pos_layout + y_delta))
        self.Bind(wx.EVT_BUTTON, self.start_monkey, self.quickButton)

        self.doButton = wx.Button(panel, -1, "开始Monkey", pos=(x_pos + 120 * 2, y_pos_layout + y_delta))
        self.Bind(wx.EVT_BUTTON, self.begin_monkey, self.doButton)

        self.captureButton = wx.Button(panel, -1, "截图", pos=(x_pos, y_pos_layout + 2 * y_delta))
        self.Bind(wx.EVT_BUTTON, self.capture_screen, self.captureButton)

        self.stopButton = wx.Button(panel, -1, "停止Monkey", pos=(x_pos + 120, y_pos_layout + 2 * y_delta))
        self.Bind(wx.EVT_BUTTON, self.stop_monkey, self.stopButton)
        self.stopButton.SetDefault()

    def on_quit(self, e):
        self.stop_monkey(e)
        self.Close()

    def get_current_activity(self):
        cmd = 'adb -s %s shell dumpsys activity | grep mFocusedActivity' % self.current_device()
        activity = commands.getstatusoutput(cmd)[1].split('ActivityRecord')[1].split('/')[1].split(' ')[0]
        return activity

    def change_activity(self):
        import random
        while 1:
            cmd = 'adb -s %s shell ps | grep monkey' % self.current_device()
            monkey_alive = commands.getstatusoutput(cmd)
            if monkey_alive[1]:
                current_activity_befor = self.get_current_activity()
                activity_list = ['HomeActivity', 'NativeActivity', 'InteractiveAdsActivity',
                                 'NativeMultemplateActivity', 'AppwallActivity', 'RewardActivity', 'FeedsActivity',
                                 'FeedsImageActivity', 'NativeInterstitialActivity', 'OfferWallActivity',
                                 'InterstitialActivity', 'InterstitialVideoActivity']
                time.sleep(300)
                current_activity_after = self.get_current_activity()
                if current_activity_after == current_activity_befor:
                    use_activity = activity_list[random.randint(0, len(activity_list) - 1)]
                    pkg_name = 'com.mintegral.sdk.demo'
                    cmd = 'adb shell am start -n %s' % pkg_name + '/.' + use_activity
                    commands.getstatusoutput(cmd)
                    log.info("Current Activity: " + current_activity_befor + " chang to new activity: " +
                             pkg_name + '/.' + use_activity)

    def check_box(self, e):
        pass

    def onChecked(self, e):
        if self.checkBox.IsChecked():
            self.start_new_thread(self.change_activity)

    @staticmethod
    def get_devices():
        devices_list = []
        if check_devices():
            d_list = commands.getstatusoutput('adb devices')
            result = d_list[1].split('\n')[1:]
            for info in result:
                phone_name = info.split('\t')[0]
                if phone_name != "":
                    cmd = 'adb -s %s -d shell getprop ro.product.model' % phone_name
                    device_type = commands.getoutput(cmd).strip()
                    devices_list.append(' - '.join([device_type, phone_name]))
        return devices_list

    def get_connect_devices(self, event):
        self.listBox.Clear()
        d_list = self.get_devices()
        self.listBox.SetItems(d_list)
        if d_list.__len__() > 0:
            self.listBox.SetSelection(0)

    def current_device(self):
        return self.listBox.GetStringSelection().split(' - ')[1]

    @staticmethod
    def input_check(value):
        if value == '':
            return True
        elif all(x in '0123456789' for x in value):
            if '.' in value:
                if value.count('.') == 1 and value[0] != '.' and value[-1] != '.':
                    return True
                else:
                    return False
            elif len(value) >= 1 and value[0] != '0':
                return True
            else:
                return False
        else:
            return False

    def valid_seed(self, event):
        value = self.seedCtrl.GetValue().strip()
        if self.input_check(value):
            if value != '':
                self.seedCtrl.SetValue(value)
        else:
            self.seedCtrl.SetValue(self.seedDefault)

    def valid_num(self, event):
        value = self.executeNumCtrl.GetValue().strip()
        if self.input_check(value):
            if value != '':
                self.executeNumCtrl.SetValue(value)
        else:
            self.executeNumCtrl.SetValue(self.executeNumDefault)

    def valid_delay(self, event):
        value = self.delayNumCtrl.GetValue().strip()
        if self.input_check(value):
            if value != '':
                log.info('Delay_num = ' + value)
                self.delayNumCtrl.SetValue(value)
        else:
            self.delayNumCtrl.SetValue(self.delayDefault)

    def quick_monkey(self):
        self.onChecked(True)
        self.checkBox.Disable()
        self.quickButton.Disable()
        self.doButton.Disable()
        self.listBox.Disable()
        self.reset()
        self.start_cmd()

    def normal_monkey(self):
        self.onChecked(True)
        self.checkBox.Disable()
        self.quickButton.Disable()
        self.doButton.Disable()
        self.listBox.Disable()
        self.start_cmd()

    @staticmethod
    def start_new_thread(task):
        thread.start_new_thread(task, ())

    def start_monkey(self, event):
        if check_devices():
            self.start_new_thread(self.quick_monkey)
        else:
            log.warn('Please check the device connection!')

    def begin_monkey(self, event):
        if check_devices():
            self.start_new_thread(self.normal_monkey)
        else:
            log.warn('Please check the device connection!')

    def on_select_all(self, event):
        list_string = self.checkListBox
        count = list_string.GetCount()
        array = []
        for i in range(0, count):
            array.append(i)
        list_string.SetCheckedItems(array)

    def on_unselect(self, event):
        self.checkListBox.SetCheckedItems([])

    def on_reset(self, event):
        self.reset()

    def get_package_list(self, event):
        self.checkListBox.Clear()
        cmd = "adb -s %s shell pm list packages" % self.current_device()
        result = commands.getoutput(cmd).split('\n')
        while '' in result:
            result.remove('')
        if len(result) > 1:
            for item in result:
                if item != "":
                    pkg = item.split(':')[1]
                    self.checkListBox.Append(pkg.strip())
                else:
                    self.checkListBox.Append(self.default_package)
        elif len(result) == 1:
            if 'Permission' in result[0]:
                log.warn('Need ROOT Permission to access!')
                self.checkListBox.Append(self.default_package)
            else:
                self.checkListBox.Append(result[0].split(':')[1].strip())

    def reset(self):
        self.seedCtrl.SetValue(self.seedDefault)
        self.executeNumCtrl.SetValue(self.executeNumDefault)
        self.delayNumCtrl.SetValue(self.delayDefault)
        self.executeModeCtrl.SetSelection(0)
        self.logModeCtrl.SetSelection(2)

    def start_cmd(self):
        seed = self.seedCtrl.GetValue()
        execute_num = self.executeNumCtrl.GetValue()
        delay_num = self.delayNumCtrl.GetValue()
        # execute_mode = self.executeModeCtrl.GetValue()
        date = time.strftime('%Y%m%d%H%m%s', time.localtime(time.time()))
        package_section = ""

        if self.checkListBox.GetCheckedStrings():
            package_list = self.checkListBox.GetCheckedStrings()
        else:
            package_list = self.default_package
        log.info("Selected package count: %d" % len(package_list))
        for item in package_list:
            pack = item.strip('\r\n')
            log.info('         Package: %s' % pack)
            package_section += (" -p " + pack)

        main_device = self.current_device()

        seed_section = " -s " + seed
        delay_section = " --throttle " + delay_num
        log_section = ""

        touch_section = ' --pct-touch 10'
        motion_section = ' --pct-motion 0'
        hard_key_section = ' --pct-anyevent 0'
        system_key_section = ' --pct-syskeys 0'
        activity_p_section = ' --pct-appswitch 0'

        log_level = self.logModeCtrl.GetSelection()
        if log_level == 0:
            log_section += " -v"
        elif log_level == 1:
            log_section += " -v -v"
        elif log_level == 2:
            log_section += " -v -v -v"

        mode_id = self.executeModeCtrl.GetSelection()
        mode = ["",
                " --ignore-crashes",
                " --ignore-timeouts",
                " --ignore-security-exceptions",
                " --ignore-native-crashes",
                " --monitor-native-crashes"]
        if mode_id == 1:
            execute_mode_section = mode[1]
        elif mode_id == 2:
            execute_mode_section = mode[2]
        elif mode_id == 3:
            execute_mode_section = mode[3]
        elif mode_id == 4:
            execute_mode_section = mode[4]
        elif mode_id == 5:
            execute_mode_section = mode[5]
        else:
            execute_mode_section = mode[1] + mode[2] + mode[3] + mode[4] + mode[5]

        # create monkey log dir ###############
        if not os.path.isdir('./MonkeyLog/'):
            os.mkdir('./MonkeyLog/')
        os.chdir('./MonkeyLog/')
        log_home = os.getcwd()
        log_name = "MonkeyLog_" + date
        os.mkdir(log_name)
        self.log_dir = os.path.join(log_home, log_name)
        log.info(self.log_dir)
        os.chdir(self.log_dir)

        # run monkey and record monkey log ################
        monkey_cmd = "adb -s %s shell monkey" % main_device
        monkey_cmd = monkey_cmd + delay_section + seed_section + package_section + touch_section\
                     + motion_section + hard_key_section + system_key_section + activity_p_section + log_section\
                     + execute_mode_section
        monkey_cmd = monkey_cmd + " " + execute_num + " > monkey.log"
        log.info(monkey_cmd)
        commands.getstatusoutput(monkey_cmd)
        log.info('#' * 15 + ' Monkey finish '+'#' * 15)
        os.chdir(self.root_dir)
        self.quickButton.Enable()
        self.doButton.Enable()
        self.listBox.Enable()

    @staticmethod
    def build_log(path):
        for root, dirs, files in os.walk(path):
            for f in files:
                if f.find("logcat.txt") == 0:
                    log_f = f.strip()
                    os.chdir(root)
                    if log_f != "":
                        grep_cmd = "grep -Eni -B30 -A30 'FATAL|error|exception|system.err|androidruntime' " + log_f + \
                                   " > " + log_f.split('.')[0] + str(time.time()) + "_fatal.log"
                        os.system(grep_cmd)
        log.info('#' * 15 + ' Log build finish ' + '#' * 15)

    def save_logcat(self, event):
        os.chdir(self.log_dir)
        self.start_new_thread(self.save_log)

    def stop_logcat(self, event):
        if check_devices():
            self.logcat_p = commands.getoutput('adb -s %s shell ps | grep logcat' % self.current_device())
            if self.logcat_p != "":
                for i in self.logcat_p.strip().split('\r'):
                    pid = self.remove_item(i.split(' '), '')[1]
                    log.info('Logcat pid = ' + pid)
                    commands.getoutput('adb -s %s shell kill %s' % (self.current_device(), pid))
            else:
                log.info('No logcat process running!')

    def clear_logcat(self):
        cmd = 'adb -s %s logcat -c' % self.current_device()
        commands.getstatusoutput(cmd)

    def save_log(self):
        self.clear_logcat()
        cmd = 'adb -s %s logcat -v time > logcat.txt' % self.current_device()
        commands.getstatusoutput(cmd)

    def build_fatal_log(self, event):
        self.stop_logcat(event)
        self.build_log(self.log_dir)

    def check_monkey(self, event):
        if check_devices():
            self.monkey_p = commands.getoutput('adb -s %s shell ps | grep monkey' % self.current_device())
            if self.monkey_p != "":
                pid = self.remove_item(self.monkey_p.split(' '), '')[1]
                log.info('Monkey pid = ' + pid)
                return True, pid
            else:
                log.info('No monkey process running!')
                return False

    @staticmethod
    def remove_item(iter_obj, item):
        tmp = iter_obj
        if isinstance(iter_obj, str):
            tmp = iter_obj.replace(item, '')
        elif hasattr(iter_obj, '__iter__'):
            while item in iter_obj:
                if isinstance(iter_obj, dict):
                    del iter_obj[item]
                elif isinstance(iter_obj, list):
                    iter_obj.remove(item)
                elif isinstance(iter_obj, tuple):
                    break
                tmp = iter_obj
        return tmp

    def stop_monkey(self, event):
        monkey_event = self.check_monkey(event)
        if monkey_event:
            pid = monkey_event[1]
            commands.getoutput('adb -s %s shell kill %s' % (self.current_device(), pid))
            self.stop_logcat(event)
        self.quickButton.Enable()
        self.doButton.Enable()
        self.listBox.Enable()
        self.checkBox.Enable()
        os.chdir(self.root_dir)

    def capture_task(self):
        try:
            self.start_new_thread(take_screen_shot(device=self.current_device(), file_name='Capture_'+str(time.time())))
        except MyException, e:
            img_path = e.message
            if img_path:
                img = Image.open(img_path)
                img.show()
        else:
            pass

    def capture_screen(self, event):
        self.start_new_thread(self.capture_task)


if __name__ == '__main__':
    app = wx.App()
    frame = MainFrame()
    frame.Show(True)
    app.MainLoop()
