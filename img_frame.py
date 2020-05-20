#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/9/10 下午9:05
# @Author  : Huang Jincheng
# @Site    : 
# @File    : img_frame.py
# @Software: PyCharm
import wx


class Panel(wx.Panel):
    """ class Panel1 creates a panel with an image on it, inherits wx.Panel """

    def __init__(self, img_file, parent, id):

        wx.Panel.__init__(self, parent, id)
        try:
            img = wx.Image(img_file, wx.BITMAP_TYPE_ANY)
            w = img.GetWidth()
            h = img.GetHeight()
            wx.StaticBitmap(self, -1, self.resize_bitmap(img, w/4, h/4))
        except IOError:
            print "Image file [%s] not found" % img_file
            raise SystemExit

    @staticmethod
    def resize_bitmap(image, width, height):
        bmp = image.Scale(width, height).ConvertToBitmap()
        return bmp


if __name__ == "__main__":
    img_path = "img.jpg"
    img_frame = wx.Frame(None, -1, "Image Viewer", style=wx.CLOSE_BOX, size=(382, 661))
    Panel(img_path, img_frame, 1)
    img_frame.Show(1)
