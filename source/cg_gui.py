#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
import cg_algorithms as alg
from typing import Optional
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    qApp,
    QGraphicsScene,
    QGraphicsView,
    QGraphicsItem,
    QListWidget,
    QHBoxLayout,
    QWidget,
    QStyleOptionGraphicsItem,
    QLabel,
    QColorDialog,
    QFileDialog)
from PyQt5.QtGui import QPainter, QMouseEvent, QColor, QIcon, QImage
from PyQt5.QtCore import QRectF


class MyCanvas(QGraphicsView):
    """
    画布窗体类，继承自QGraphicsView，采用QGraphicsView、QGraphicsScene、QGraphicsItem的绘图框架
    """
    def __init__(self, *args):
        super().__init__(*args)
        self.main_window = None
        self.list_widget = None
        self.item_dict = {}
        self.selected_id = ''

        self.status = ''
        self.temp_algorithm = ''
        self.temp_id = ''
        self.temp_item = None
        
        self.is_drawing = False
        self.setMouseTracking(True)
        self.pen_color = QColor(0, 0, 0)

    def start_draw_line(self, algorithm, item_id):
        self.status = 'line'
        self.temp_algorithm = algorithm
        self.temp_id = item_id

    def start_draw_polygon(self, algorithm, item_id):
        self.status = 'polygon'
        self.temp_algorithm = algorithm
        self.temp_id = item_id

    def start_draw_ellipse(self, item_id):
        self.status = 'ellipse'
        self.temp_id = item_id

    def start_draw_curve(self, algorithm, item_id):
        self.status = 'curve'
        self.temp_algorithm = algorithm
        self.temp_id = item_id
    
    # TODO: start_draw $other graphic$

    def finish_draw(self):
        self.temp_id = self.main_window.get_id()
        self.is_drawing = False

    def clear_selection(self):
        if self.selected_id != '':
            self.item_dict[self.selected_id].selected = False
            self.selected_id = ''

    def selection_changed(self, selected):
        self.main_window.statusBar().showMessage('图元选择： %s' % selected)
        if self.selected_id != '':
            self.item_dict[self.selected_id].selected = False
            self.item_dict[self.selected_id].update()
        self.selected_id = selected
        self.item_dict[selected].selected = True
        self.item_dict[selected].update()
        self.status = ''
        self.updateScene([self.sceneRect()])

    def mousePressEvent(self, event: QMouseEvent) -> None:
        pos = self.mapToScene(event.localPos().toPoint())
        flag = event.button()   # no: 0; left: 1; right: 2; middle 4; side4: 16
        x = int(pos.x())
        y = int(pos.y())
        if self.status == 'line':
            self.is_drawing = True
            self.temp_item = MyItem(self.temp_id, self.status, [[x, y], [x, y]], self.pen_color, self.temp_algorithm)
            self.scene().addItem(self.temp_item)
        elif self.status == 'polygon':
            if not self.is_drawing:               # start drawing
                self.is_drawing = True
                self.temp_item = MyItem(self.temp_id, self.status, [[x, y]], self.pen_color, self.temp_algorithm)
                self.scene().addItem(self.temp_item)
        elif self.status == 'ellipse':
            self.is_drawing = True
            self.temp_item = MyItem(self.temp_id, self.status, [[x, y], [x, y]], self.pen_color)
            self.scene().addItem(self.temp_item)
        elif self.status == 'curve' and self.temp_algorithm == 'Bezier':
            if not self.is_drawing:
                self.is_drawing = True
                self.temp_item = MyItem(self.temp_id, self.status, [[x, y]], self.pen_color, self.temp_algorithm)
                self.scene().addItem(self.temp_item)
        # TODO: other status 
        self.updateScene([self.sceneRect()])
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        pos = self.mapToScene(event.localPos().toPoint())
        x = int(pos.x())
        y = int(pos.y())
        if self.status == 'line' and self.is_drawing:
            self.temp_item.p_list[1] = [x, y]
        elif self.status == 'polygon' and self.is_drawing:
            self.temp_item.p_list[-1] = [x, y]
        elif self.status == 'ellipse' and self.is_drawing:
            self.temp_item.p_list[1] = [x, y]
        elif self.status == 'curve' and self.temp_algorithm == 'Bezier' and self.is_drawing:
            self.temp_item.p_list[-1] = [x, y]
        # TODO: other status
        self.updateScene([self.sceneRect()])
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        pos = self.mapToScene(event.localPos().toPoint())
        flag = event.button()   # no: 0; left: 1; right: 2; middle 4; side4: 16
        x = int(pos.x())
        y = int(pos.y())
        if self.status == 'line':
            self.is_drawing = False
            self.item_dict[self.temp_id] = self.temp_item
            self.list_widget.addItem(self.temp_id)
            self.finish_draw()
        elif self.status == 'polygon':
            if self.is_drawing:
                if flag == 2:   # right click: finish one polygon
                    self.item_dict[self.temp_id] = self.temp_item
                    self.list_widget.addItem(self.temp_id)
                    self.finish_draw()
                else:           # other click: add vertex
                    self.temp_item.p_list.append( [x, y] )
        elif self.status == 'ellipse':
            self.is_drawing = False
            self.item_dict[self.temp_id] = self.temp_item
            self.list_widget.addItem(self.temp_id)
            self.finish_draw()
        elif self.status == 'curve' and self.temp_algorithm == 'Bezier':
            if self.is_drawing:
                if flag == 2:
                    self.item_dict[self.temp_id] = self.temp_item
                    self.list_widget.addItem(self.temp_id)
                    self.finish_draw()
                else:
                    self.temp_item.p_list.append( [x, y] )
        # TODO: other status
        super().mouseReleaseEvent(event)

    def mycanvas_to_QImage(self):

        area = self.sceneRect()

        # Create image and painter to render
        temp_image = QImage(area.width(), area.height(), QImage.Format_ARGB32_Premultiplied)
        temp_painter = QPainter(temp_image)

        # Render area to image
        self.scene().render(temp_painter, QRectF(temp_image.rect()), area)
        temp_painter.end()

        return temp_image

class MyItem(QGraphicsItem):
    """
    自定义图元类，继承自QGraphicsItem
    """
    def __init__(self, item_id: str, item_type: str, p_list: list, pen_color: QColor, algorithm: str = '', parent: QGraphicsItem = None):
        """

        :param item_id: 图元ID
        :param item_type: 图元类型，'line'、'polygon'、'ellipse'、'curve'等
        :param p_list: 图元参数
        :param algorithm: 绘制算法，'DDA'、'Bresenham'、'Bezier'、'B-spline'等
        :param parent:
        """
        super().__init__(parent)
        self.id = item_id           # 图元ID
        self.item_type = item_type  # 图元类型，'line'、'polygon'、'ellipse'、'curve'等
        self.p_list = p_list        # 图元参数
        self.algorithm = algorithm  # 绘制算法，'DDA'、'Bresenham'、'Bezier'、'B-spline'等
        self.selected = False
        self.item_pen_color = pen_color

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: Optional[QWidget] = ...) -> None:
        if self.item_type == 'line':
            item_pixels = alg.draw_line(self.p_list, self.algorithm)
            for p in item_pixels:
                painter.setPen(self.item_pen_color)
                painter.drawPoint(*p)
            if self.selected:
                painter.setPen(QColor(255, 0, 0))
                painter.drawRect(self.boundingRect())
        elif self.item_type == 'polygon':
            item_pixels = alg.draw_polygon(self.p_list, self.algorithm)
            for p in item_pixels:
                painter.setPen(self.item_pen_color)
                painter.drawPoint(*p)
            if self.selected:
                painter.setPen(QColor(255, 0, 0))
                painter.drawRect(self.boundingRect())
        elif self.item_type == 'ellipse':
            item_pixels = alg.draw_ellipse(self.p_list)
            for p in item_pixels:
                painter.setPen(self.item_pen_color)
                painter.drawPoint(*p)
            if self.selected:
                painter.setPen(QColor(255, 0, 0))
                painter.drawRect(self.boundingRect())
        elif self.item_type == 'curve':
            item_pixels = alg.draw_curve(self.p_list, self.algorithm)
            for p in item_pixels:
                painter.setPen(self.item_pen_color)
                painter.drawPoint(*p)
            if self.selected:
                painter.setPen(QColor(255, 0, 0))
                painter.drawRect(self.boundingRect())
        # TODO:    ??

    def boundingRect(self) -> QRectF:
        if self.item_type == 'line':
            x0, y0 = self.p_list[0]
            x1, y1 = self.p_list[1]
            x = min(x0, x1)
            y = min(y0, y1)
            w = max(x0, x1) - x
            h = max(y0, y1) - y
            return QRectF(x - 1, y - 1, w + 2, h + 2)
        # TODO:
        elif self.item_type == 'polygon':
            (xmin, ymin) = self.p_list[0]
            (xmax, ymax) = self.p_list[0]
            for (x, y) in self.p_list:
                if x < xmin:
                    xmin = x
                if x > xmax:
                    xmax = x
                if y < ymin:
                    ymin = y
                if y > ymax:
                    ymax = y
            w = xmax - xmin
            h = ymax - ymin
            return QRectF(xmin - 1, ymin - 1, w + 2, h + 2)

        elif self.item_type == 'ellipse':
            x0, y0 = self.p_list[0]
            x1, y1 = self.p_list[1]
            x = min(x0, x1)
            y = min(y0, y1)
            w = max(x0, x1) - x
            h = max(y0, y1) - y
            return QRectF(x - 1, y - 1, w + 2, h + 2)
        elif self.item_type == 'curve':
            all_pixels = alg.draw_curve(self.p_list, self.algorithm)
            (xmin, ymin) = all_pixels[0]
            (xmax, ymax) = all_pixels[0]
            for (x, y) in all_pixels:
                if x < xmin:
                    xmin = x
                if x > xmax:
                    xmax = x
                if y < ymin:
                    ymin = y
                if y > ymax:
                    ymax = y
            w = xmax - xmin
            h = ymax - ymin
            return QRectF(xmin - 1, ymin - 1, w + 2, h + 2)

class MainWindow(QMainWindow):
    """
    主窗口类
    """
    def __init__(self):
        super().__init__()
        self.item_cnt = 0

        # 使用QListWidget来记录已有的图元，并用于选择图元。注：这是图元选择的简单实现方法，更好的实现是在画布中直接用鼠标选择图元
        self.list_widget = QListWidget(self)
        self.list_widget.setMinimumWidth(200)

        # 使用QGraphicsView作为画布
        self.scene = QGraphicsScene(self)
        self.scene.setSceneRect(0, 0, 600, 600)
        self.canvas_widget = MyCanvas(self.scene, self)
        self.canvas_widget.setFixedSize(600, 600)
        self.canvas_widget.main_window = self
        self.canvas_widget.list_widget = self.list_widget


        # 设置菜单栏
        menubar = self.menuBar()
        file_menu = menubar.addMenu('文件')
        set_pen_act = file_menu.addAction('设置画笔')
        reset_canvas_act = file_menu.addAction('重置画布')
        save_canvas_act = file_menu.addAction('保存画布')
        exit_act = file_menu.addAction('退出')
        draw_menu = menubar.addMenu('绘制')
        line_menu = draw_menu.addMenu('线段')
        line_naive_act = line_menu.addAction('Naive')
        line_dda_act = line_menu.addAction('DDA')
        line_bresenham_act = line_menu.addAction('Bresenham')
        polygon_menu = draw_menu.addMenu('多边形')
        polygon_dda_act = polygon_menu.addAction('DDA')
        polygon_bresenham_act = polygon_menu.addAction('Bresenham')
        ellipse_act = draw_menu.addAction('椭圆')
        curve_menu = draw_menu.addMenu('曲线')
        curve_bezier_act = curve_menu.addAction('Bezier')
        curve_b_spline_act = curve_menu.addAction('B-spline')
        edit_menu = menubar.addMenu('编辑')
        translate_act = edit_menu.addAction('平移')
        rotate_act = edit_menu.addAction('旋转')
        scale_act = edit_menu.addAction('缩放')
        clip_menu = edit_menu.addMenu('裁剪')
        clip_cohen_sutherland_act = clip_menu.addAction('Cohen-Sutherland')
        clip_liang_barsky_act = clip_menu.addAction('Liang-Barsky')

        # 连接信号和槽函数
        exit_act.triggered.connect(qApp.quit)
        set_pen_act.triggered.connect(self.set_pen_action)
        reset_canvas_act.triggered.connect(self.reset_canvas_action)
        save_canvas_act.triggered.connect(self.save_canvas_action)
            # line funcs
        line_naive_act.triggered.connect(self.line_naive_action)
        line_dda_act.triggered.connect(self.line_dda_action)
        line_bresenham_act.triggered.connect(self.line_bresenham_action)
            # polygon funcs
        polygon_dda_act.triggered.connect(self.polygon_dda_action)
        polygon_bresenham_act.triggered.connect(self.polygon_bresenham_action)
            # ellipse funcs
        ellipse_act.triggered.connect(self.ellipse_action)
            # curve funcs
        curve_bezier_act.triggered.connect(self.curve_bezier_action)
        # TODO: other func link
            # select funcs
        self.list_widget.currentTextChanged.connect(self.canvas_widget.selection_changed)

        # 设置主窗口的布局
        self.hbox_layout = QHBoxLayout()
        self.hbox_layout.addWidget(self.canvas_widget)
        self.hbox_layout.addWidget(self.list_widget, stretch=1)
        self.central_widget = QWidget()
        self.central_widget.setLayout(self.hbox_layout)
        self.setCentralWidget(self.central_widget)
        self.statusBar().showMessage('空闲')
        self.resize(600, 600)
        self.setWindowTitle('CG application - by 曾许曌秋(https://zxzq.me)')
        self.setWindowIcon(QIcon("./pics/favicon.ico"))

    def get_id(self):
        _id = str(self.item_cnt)
        self.item_cnt += 1
        return _id

    def set_pen_action(self):
        self.canvas_widget.pen_color = QColorDialog.getColor()
        self.statusBar().showMessage('Pen color selected: %s' % self.canvas_widget.pen_color.name())

    def reset_canvas_action(self):
        self.scene.clear()
        self.list_widget.clear()
        self.item_cnt = 0
        self.canvas_widget.item_dict = {}

    def save_canvas_action(self):
        # select savepath
        save_path, _ = QFileDialog.getSaveFileName(self, "Save Image", "", "PNG(*.png);;JPEG(*.jpg *.jpeg);;All Files(*.*) ")

        # if path is blank exit
        if save_path == "":
            return
        
        # get image and save
        self.canvas_widget.mycanvas_to_QImage().save(save_path)

    def line_naive_action(self):
        self.canvas_widget.start_draw_line('Naive', self.get_id())
        self.statusBar().showMessage('Naive算法绘制线段')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def line_dda_action(self):
        self.canvas_widget.start_draw_line('DDA', self.get_id())
        self.statusBar().showMessage('DDA算法绘制线段')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def line_bresenham_action(self):
        self.canvas_widget.start_draw_line('Bresenham', self.get_id())
        self.statusBar().showMessage('Bresenham算法绘制线段')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def polygon_dda_action(self):
        self.canvas_widget.start_draw_polygon('DDA', self.get_id())
        self.statusBar().showMessage('DDA算法绘制多边形，右键结束')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def polygon_bresenham_action(self):
        self.canvas_widget.start_draw_polygon('Bresenham', self.get_id())
        self.statusBar().showMessage('Bresenham算法绘制多边形，右键结束')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()


    def ellipse_action(self):
        self.canvas_widget.start_draw_ellipse(self.get_id())
        self.statusBar().showMessage('绘制椭圆')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def curve_bezier_action(self):
        self.canvas_widget.start_draw_curve('Bezier', self.get_id())
        self.statusBar().showMessage('Bezier曲线绘制,单击添加控制点，右键结束')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    # TODO: realise other action funcs


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec_())
