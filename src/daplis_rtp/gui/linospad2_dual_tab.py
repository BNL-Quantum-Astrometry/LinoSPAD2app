"""Tab for real-time plotting of the full LinoSPAD2 sensor (2 × 256 pixels).

Layout mirrors the single-board "Online plot" tab.  The left frame holds
two stacked browse rows (one per board), the plot, and the two spin boxes
holding the x-axis limits (0-511, spanning both halves).  The right frame
holds all controls: shared daughterboard/firmware/timestamps selectors,
two motherboard selectors, a shared preset-mask checkbox and reset
button, and the pixel-mask area split into two side-by-side scroll areas
(board 1 left, board 2 right) that together occupy the same space as the
single scroll area in the original tab.

Pixel-address correction is always applied to board 2 (never to board 1)
as required by the sensor geometry; no UI control is exposed for this.
The same holds for the absolute timestamps: full-sensor data are always
collected with them, as they are needed to synchronize the two boards,
so they are always unpacked here.

"""

import glob
import os
from importlib.resources import files

import numpy as np
from PyQt5 import QtCore, QtGui, QtWidgets

from daplis_rtp.functions.sen_pop import sen_pop
from daplis_rtp.gui.plot_figure_dual import PltCanvasDual


class LinoSPAD2Dual(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        font10 = QtGui.QFont()
        font10.setPointSize(10)
        font_bold = QtGui.QFont()
        font_bold.setPointSize(10)
        font_bold.setBold(True)
        font_bold.setWeight(75)

        # ------------------------------------------------------------------
        # Outer grid: frame (col 0, expanding) | frame_2 (col 1, fixed)
        # ------------------------------------------------------------------
        self.gridLayout_2 = QtWidgets.QGridLayout(self)
        self.gridLayout_2.setObjectName("gridLayout_2")

        # ==================================================================
        # RIGHT FRAME (frame_2) — all controls
        # ==================================================================
        self.frame_2 = QtWidgets.QFrame(self)
        sp_fixed = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred
        )
        self.frame_2.setSizePolicy(sp_fixed)
        self.frame_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_2.setObjectName("frame_2")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.frame_2)
        self.verticalLayout.setObjectName("verticalLayout")

        # --- Daughterboard (shared) ---
        hl_db = QtWidgets.QHBoxLayout()
        hl_db.setObjectName("horizontalLayout_db")
        lbl_db = QtWidgets.QLabel("LinoSPAD2 daughterboard", self.frame_2)
        lbl_db.setFont(font10)
        lbl_db.setMinimumSize(QtCore.QSize(0, 26))
        hl_db.addWidget(lbl_db)
        self.comboBox_mask_2 = QtWidgets.QComboBox(self.frame_2)
        self.comboBox_mask_2.setFont(font10)
        self.comboBox_mask_2.setMinimumSize(QtCore.QSize(80, 0))
        self.comboBox_mask_2.setEditable(True)
        self.comboBox_mask_2.setInsertPolicy(
            QtWidgets.QComboBox.InsertAtCurrent
        )
        for item in ["B7d", "NL11", "A5", "D2b"]:
            self.comboBox_mask_2.addItem(item)
        hl_db.addWidget(self.comboBox_mask_2)
        self.verticalLayout.addLayout(hl_db)

        # --- Motherboard Board 1 ---
        hl_mb1 = QtWidgets.QHBoxLayout()
        hl_mb1.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
        hl_mb1.setContentsMargins(-1, 0, -1, 0)
        lbl_mb1 = QtWidgets.QLabel("Motherboard Board 1", self.frame_2)
        lbl_mb1.setFont(font10)
        lbl_mb1.setMinimumSize(QtCore.QSize(0, 26))
        hl_mb1.addWidget(lbl_mb1)
        self.comboBox_mb_1 = QtWidgets.QComboBox(self.frame_2)
        self.comboBox_mb_1.setFont(font10)
        self.comboBox_mb_1.setMinimumSize(QtCore.QSize(80, 0))
        self.comboBox_mb_1.setEditable(True)
        self.comboBox_mb_1.setInsertPolicy(QtWidgets.QComboBox.InsertAtCurrent)
        for item in ["#28", "#33", "#21", "#36", "#37", "#4", "#29"]:
            self.comboBox_mb_1.addItem(item)
        hl_mb1.addWidget(self.comboBox_mb_1)
        self.verticalLayout.addLayout(hl_mb1)

        # --- Motherboard Board 2 ---
        hl_mb2 = QtWidgets.QHBoxLayout()
        hl_mb2.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
        hl_mb2.setContentsMargins(-1, 0, -1, 0)
        lbl_mb2 = QtWidgets.QLabel("Motherboard Board 2", self.frame_2)
        lbl_mb2.setFont(font10)
        lbl_mb2.setMinimumSize(QtCore.QSize(0, 26))
        hl_mb2.addWidget(lbl_mb2)
        self.comboBox_mb_2 = QtWidgets.QComboBox(self.frame_2)
        self.comboBox_mb_2.setFont(font10)
        self.comboBox_mb_2.setMinimumSize(QtCore.QSize(80, 0))
        self.comboBox_mb_2.setEditable(True)
        self.comboBox_mb_2.setInsertPolicy(QtWidgets.QComboBox.InsertAtCurrent)
        for item in ["#28", "#33", "#21", "#36", "#37", "#4", "#29"]:
            self.comboBox_mb_2.addItem(item)
        hl_mb2.addWidget(self.comboBox_mb_2)
        self.verticalLayout.addLayout(hl_mb2)

        # --- Firmware (shared) ---
        hl_fw = QtWidgets.QHBoxLayout()
        hl_fw.setContentsMargins(-1, -1, -1, 0)
        lbl_fw = QtWidgets.QLabel("Firmware version", self.frame_2)
        lbl_fw.setFont(font10)
        lbl_fw.setMinimumSize(QtCore.QSize(0, 26))
        hl_fw.addWidget(lbl_fw)
        self.comboBox_FW_2 = QtWidgets.QComboBox(self.frame_2)
        self.comboBox_FW_2.setFont(font10)
        self.comboBox_FW_2.setMinimumSize(QtCore.QSize(80, 0))
        for item in ["2212b", "2208", "2212s"]:
            self.comboBox_FW_2.addItem(item)
        hl_fw.addWidget(self.comboBox_FW_2)
        self.verticalLayout.addLayout(hl_fw)

        # --- Timestamps (shared) ---
        hl_ts = QtWidgets.QHBoxLayout()
        lbl_ts = QtWidgets.QLabel("Timestamps", self.frame_2)
        lbl_ts.setFont(font10)
        lbl_ts.setMinimumSize(QtCore.QSize(0, 26))
        lbl_ts.setToolTip(
            "Number of timestamps per pixel per acquisition cycle."
        )
        hl_ts.addWidget(lbl_ts)
        self.spinBox_timestamps_2 = QtWidgets.QSpinBox(self.frame_2)
        self.spinBox_timestamps_2.setFont(font10)
        self.spinBox_timestamps_2.setMinimumSize(QtCore.QSize(80, 0))
        self.spinBox_timestamps_2.setMaximum(1536)
        self.spinBox_timestamps_2.setValue(300)
        hl_ts.addWidget(self.spinBox_timestamps_2)
        self.verticalLayout.addLayout(hl_ts)

        # --- Preset mask + Reset (both boards) ---
        hl_pmask = QtWidgets.QHBoxLayout()
        hl_pmask.setContentsMargins(-1, 0, -1, 0)
        self.checkBox_presetMask_2 = QtWidgets.QCheckBox(
            "Preset mask", self.frame_2
        )
        self.checkBox_presetMask_2.setFont(font10)
        self.checkBox_presetMask_2.setMinimumSize(QtCore.QSize(0, 26))
        hl_pmask.addWidget(self.checkBox_presetMask_2)
        self.label_presetMaskInfo_2 = QtWidgets.QLabel("i", self.frame_2)
        self.label_presetMaskInfo_2.setMinimumSize(QtCore.QSize(20, 20))
        self.label_presetMaskInfo_2.setMaximumSize(QtCore.QSize(20, 20))
        self.label_presetMaskInfo_2.setFont(font10)
        self.label_presetMaskInfo_2.setFrameShape(QtWidgets.QFrame.Box)
        self.label_presetMaskInfo_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_presetMaskInfo_2.setToolTip(
            "Applies the warm-pixel mask for both boards using their "
            "respective motherboard numbers."
        )
        hl_pmask.addWidget(self.label_presetMaskInfo_2)
        hl_pmask.addItem(
            QtWidgets.QSpacerItem(
                5,
                20,
                QtWidgets.QSizePolicy.Expanding,
                QtWidgets.QSizePolicy.Minimum,
            )
        )
        self.pushButton_resetMask_2 = QtWidgets.QPushButton(
            "Reset Mask", self.frame_2
        )
        self.pushButton_resetMask_2.setFont(font10)
        self.pushButton_resetMask_2.setMinimumSize(QtCore.QSize(90, 21))
        hl_pmask.addWidget(self.pushButton_resetMask_2)
        self.verticalLayout.addLayout(hl_pmask)

        # --- Pixel mask: two scroll areas side by side ---
        # Board 1 left, board 2 right; each 2 columns × 128 rows.
        # Combined width ≈ original 4-column scroll area.
        hl_scrolls = QtWidgets.QHBoxLayout()

        self.scrollArea = QtWidgets.QScrollArea(self.frame_2)
        self.scrollArea.setMinimumSize(QtCore.QSize(0, 250))
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 140, 300))
        self.scrollAreaWidgetContentslayout = QtWidgets.QGridLayout(
            self.scrollAreaWidgetContents
        )
        self.checkBoxPixel = []
        self.maskValidPixels = np.zeros(256)
        for col in range(2):
            for row in range(128):
                cb = QtWidgets.QCheckBox(
                    str(row + col * 128), self.scrollAreaWidgetContents
                )
                self.checkBoxPixel.append(cb)
                self.scrollAreaWidgetContentslayout.addWidget(
                    cb, row, col, 1, 1
                )
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.scrollArea_b2 = QtWidgets.QScrollArea(self.frame_2)
        self.scrollArea_b2.setMinimumSize(QtCore.QSize(0, 250))
        self.scrollArea_b2.setWidgetResizable(True)
        self.scrollAreaWidgetContents_b2 = QtWidgets.QWidget()
        self.scrollAreaWidgetContents_b2.setGeometry(
            QtCore.QRect(0, 0, 140, 300)
        )
        self.scrollAreaWidgetContentslayout_b2 = QtWidgets.QGridLayout(
            self.scrollAreaWidgetContents_b2
        )
        self.checkBoxPixel_b2 = []
        self.maskValidPixels_b2 = np.zeros(256)
        for col in range(2):
            for row in range(128):
                cb = QtWidgets.QCheckBox(
                    str(row + col * 128), self.scrollAreaWidgetContents_b2
                )
                self.checkBoxPixel_b2.append(cb)
                self.scrollAreaWidgetContentslayout_b2.addWidget(
                    cb, row, col, 1, 1
                )
        self.scrollAreaWidgetContents_b2.setObjectName(
            "scrollAreaWidgetContents_b2"
        )
        self.scrollArea_b2.setWidget(self.scrollAreaWidgetContents_b2)

        hl_scrolls.addWidget(self.scrollArea)
        hl_scrolls.addWidget(self.scrollArea_b2)
        self.verticalLayout.addLayout(hl_scrolls)

        # --- Linear scale + Grouping ---
        hl_opts = QtWidgets.QHBoxLayout()
        hl_opts.setContentsMargins(-1, -1, -1, 0)
        self.checkBox_linearScale_2 = QtWidgets.QCheckBox(
            "Linear scale", self.frame_2
        )
        self.checkBox_linearScale_2.setFont(font10)
        self.checkBox_linearScale_2.setChecked(True)
        hl_opts.addWidget(self.checkBox_linearScale_2)
        hl_opts.addItem(
            QtWidgets.QSpacerItem(
                40,
                20,
                QtWidgets.QSizePolicy.Expanding,
                QtWidgets.QSizePolicy.Minimum,
            )
        )
        self.checkBox_grouping_2 = QtWidgets.QCheckBox(
            "Group of 64", self.frame_2
        )
        self.checkBox_grouping_2.setFont(font10)
        self.checkBox_grouping_2.setToolTip(
            "Plot vertical lines at 64, 128, 192, 320, 384, 448."
        )
        hl_opts.addWidget(self.checkBox_grouping_2)
        self.verticalLayout.addLayout(hl_opts)

        # --- Refresh + Start stream ---
        self.pushButton_refreshPlot = QtWidgets.QPushButton(
            "Refresh plot", self.frame_2
        )
        self.pushButton_refreshPlot.setFont(font10)
        self.verticalLayout.addWidget(self.pushButton_refreshPlot)

        self.pushButton_startStream = QtWidgets.QPushButton(
            "Start stream", self.frame_2
        )
        self.pushButton_startStream.setFont(font_bold)
        self.pushButton_startStream.setMinimumSize(QtCore.QSize(0, 30))
        self.verticalLayout.addWidget(self.pushButton_startStream)

        self.gridLayout_2.addWidget(self.frame_2, 0, 1, 1, 1)

        # ==================================================================
        # LEFT FRAME (frame) — browse rows + plot + sliders
        # ==================================================================
        self.frame = QtWidgets.QFrame(self)
        sp_expand = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding
        )
        self.frame.setSizePolicy(sp_expand)
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.gridLayout = QtWidgets.QGridLayout(self.frame)
        self.gridLayout.setObjectName("gridLayout")

        # Browse row — Board 1 (row 0)
        sp_btn = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed
        )
        self.pushButton_browse_1 = QtWidgets.QPushButton("Board 1", self.frame)
        self.pushButton_browse_1.setSizePolicy(sp_btn)
        self.pushButton_browse_1.setMinimumSize(QtCore.QSize(100, 28))
        self.pushButton_browse_1.setFont(font10)
        self.gridLayout.addWidget(self.pushButton_browse_1, 0, 0, 1, 2)
        self.lineEdit_browse_1 = QtWidgets.QLineEdit(self.frame)
        self.lineEdit_browse_1.setMinimumSize(QtCore.QSize(0, 28))
        self.gridLayout.addWidget(self.lineEdit_browse_1, 0, 2, 1, 1)

        # Browse row — Board 2 (row 1)
        self.pushButton_browse_2 = QtWidgets.QPushButton("Board 2", self.frame)
        self.pushButton_browse_2.setSizePolicy(sp_btn)
        self.pushButton_browse_2.setMinimumSize(QtCore.QSize(100, 28))
        self.pushButton_browse_2.setFont(font10)
        self.gridLayout.addWidget(self.pushButton_browse_2, 1, 0, 1, 2)
        self.lineEdit_browse_2 = QtWidgets.QLineEdit(self.frame)
        self.lineEdit_browse_2.setMinimumSize(QtCore.QSize(0, 28))
        self.gridLayout.addWidget(self.lineEdit_browse_2, 1, 2, 1, 1)

        # Left x limit (row 6)
        lbl_lx = QtWidgets.QLabel("Left x limit", self.frame)
        lbl_lx.setFont(font10)
        lbl_lx.setMinimumSize(QtCore.QSize(0, 28))
        self.gridLayout.addWidget(lbl_lx, 6, 0, 1, 1)
        self.spinBox_leftXLim = QtWidgets.QSpinBox(self.frame)
        self.spinBox_leftXLim.setFont(font10)
        self.spinBox_leftXLim.setMinimumSize(QtCore.QSize(0, 28))
        self.spinBox_leftXLim.setMaximumSize(QtCore.QSize(120, 16777215))
        self.gridLayout.addWidget(self.spinBox_leftXLim, 6, 1, 1, 2)

        # Right x limit (row 8)
        lbl_rx = QtWidgets.QLabel("Right x limit", self.frame)
        lbl_rx.setFont(font10)
        lbl_rx.setMinimumSize(QtCore.QSize(0, 28))
        self.gridLayout.addWidget(lbl_rx, 8, 0, 1, 1)
        self.spinBox_rightXLim = QtWidgets.QSpinBox(self.frame)
        self.spinBox_rightXLim.setFont(font10)
        self.spinBox_rightXLim.setMinimumSize(QtCore.QSize(0, 28))
        self.spinBox_rightXLim.setMaximumSize(QtCore.QSize(120, 16777215))
        self.gridLayout.addWidget(self.spinBox_rightXLim, 8, 1, 1, 2)

        # Spacer between plot and sliders (row 5)
        self.gridLayout.addItem(
            QtWidgets.QSpacerItem(
                20,
                5,
                QtWidgets.QSizePolicy.Minimum,
                QtWidgets.QSizePolicy.Fixed,
            ),
            5,
            0,
            1,
            3,
        )

        self.gridLayout_2.addWidget(self.frame, 0, 0, 1, 1)

        self.show()

        # ------------------------------------------------------------------
        # State
        # ------------------------------------------------------------------
        self.pathtotimestamp_1 = ""
        self.pathtotimestamp_2 = ""
        self.leftPosition = 0
        self.rightPosition = 511
        self.grouping = False
        self.timerRunning = False
        self.last_file_ctime_1 = 0
        self.last_file_ctime_2 = 0
        self.canvas_fontsize = 16

        # ------------------------------------------------------------------
        # Plot widget — added programmatically (rows 2-5 of gridLayout)
        # ------------------------------------------------------------------
        self.widget_figure = PltCanvasDual()
        self.widget_figure.setObjectName("widget_figure_dual")
        self.gridLayout.addWidget(self.widget_figure, 2, 0, 3, 3)

        # ------------------------------------------------------------------
        # x-limit spin box configuration
        # ------------------------------------------------------------------
        # 0-511, not 0-255: this tab plots both sensor halves side by side,
        # so board 2 lives at pixels 256-511 and a 255 ceiling would put half
        # the sensor out of reach.
        self.spinBox_leftXLim.setRange(0, 511)
        self.spinBox_rightXLim.setRange(0, 511)
        self.spinBox_leftXLim.setValue(0)
        self.spinBox_rightXLim.setValue(511)
        # Commit on Enter/focus loss rather than on every keystroke, so a
        # part-typed number is not clamped against the other limit.
        self.spinBox_leftXLim.setKeyboardTracking(False)
        self.spinBox_rightXLim.setKeyboardTracking(False)

        # ------------------------------------------------------------------
        # Signal connections
        # ------------------------------------------------------------------
        self.pushButton_browse_1.clicked.connect(self.get_dir_1)
        self.pushButton_browse_2.clicked.connect(self.get_dir_2)
        self.lineEdit_browse_1.textChanged.connect(self.change_path_1)
        self.lineEdit_browse_2.textChanged.connect(self.change_path_2)

        self.spinBox_leftXLim.valueChanged.connect(self.slot_updateLeftXLim)
        self.spinBox_rightXLim.valueChanged.connect(self.slot_updateRightXLim)

        self.checkBox_presetMask_2.stateChanged.connect(self.presetmask_pixels)
        self.pushButton_resetMask_2.clicked.connect(self.reset_pix_mask)
        self.comboBox_mask_2.activated.connect(self.reset_pix_mask)

        self.checkBox_linearScale_2.stateChanged.connect(
            self.slot_checkplotscale_2
        )
        self.checkBox_grouping_2.stateChanged.connect(
            self.slot_checkBox_grouping_2
        )

        self.pushButton_refreshPlot.clicked.connect(self.slot_refresh)
        self.pushButton_startStream.clicked.connect(self.slot_startstream)

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_time_stamp)

    # ------------------------------------------------------------------
    # Resize — adaptive font size
    # ------------------------------------------------------------------

    def resizeEvent(self, event):
        min_width, max_width = 908, 3810
        min_fs, max_fs = 16, 40
        cw = max(min_width, min(max_width, self.size().width()))
        self.canvas_fontsize = min_fs + (
            (cw - min_width) / (max_width - min_width)
        ) * (max_fs - min_fs)
        self.widget_figure.setplotparameters(fontsize=self.canvas_fontsize)
        super().resizeEvent(event)

    # ------------------------------------------------------------------
    # Browse / path
    # ------------------------------------------------------------------

    def get_dir_1(self):
        path = str(
            QtWidgets.QFileDialog.getExistingDirectory(
                self, "Select Directory — Board 1"
            )
        )
        self.lineEdit_browse_1.setText(path)
        self.pathtotimestamp_1 = path

    def get_dir_2(self):
        path = str(
            QtWidgets.QFileDialog.getExistingDirectory(
                self, "Select Directory — Board 2"
            )
        )
        self.lineEdit_browse_2.setText(path)
        self.pathtotimestamp_2 = path

    def change_path_1(self):
        self.pathtotimestamp_1 = self.lineEdit_browse_1.text()

    def change_path_2(self):
        self.pathtotimestamp_2 = self.lineEdit_browse_2.text()

    # ------------------------------------------------------------------
    # Stream / refresh
    # ------------------------------------------------------------------

    def slot_startstream(self):
        self.last_file_ctime_1 = 0
        self.last_file_ctime_2 = 0
        if self.timerRunning:
            self.timer.stop()
            self.timerRunning = False
            self.pushButton_startStream.setText("Start stream")
        else:
            self.pushButton_startStream.setText("Stop stream")
            self.timer.start(100)
            self.timerRunning = True

    def slot_stopstream(self):
        self.timer.stop()
        self.timerRunning = False
        self.pushButton_startStream.setText("Start stream")
        self.last_file_ctime_1 = 0
        self.last_file_ctime_2 = 0

    def slot_refresh(self):
        self.last_file_ctime_1 = 0
        self.last_file_ctime_2 = 0
        self.update_time_stamp()

    # ------------------------------------------------------------------
    # x-axis limits
    # ------------------------------------------------------------------

    def slot_updateLeftXLim(self):
        if self.spinBox_leftXLim.value() >= self.spinBox_rightXLim.value():
            self.spinBox_leftXLim.setValue(self.spinBox_rightXLim.value() - 1)
        self.leftPosition = self.spinBox_leftXLim.value()

    def slot_updateRightXLim(self):
        if self.spinBox_rightXLim.value() <= self.spinBox_leftXLim.value():
            self.spinBox_rightXLim.setValue(self.spinBox_leftXLim.value() + 1)
        self.rightPosition = self.spinBox_rightXLim.value()

    # ------------------------------------------------------------------
    # Display options
    # ------------------------------------------------------------------

    def slot_checkplotscale_2(self):
        self.widget_figure.setPlotScale(
            self.checkBox_linearScale_2.isChecked()
        )

    def slot_checkBox_grouping_2(self):
        self.grouping = self.checkBox_grouping_2.isChecked()

    # ------------------------------------------------------------------
    # Data update
    # ------------------------------------------------------------------

    def update_time_stamp(self):
        stopping = False
        self.mask_pixels()

        DATA_FILES_1 = glob.glob(
            os.path.join(self.pathtotimestamp_1, "*.dat*")
        )
        DATA_FILES_2 = glob.glob(
            os.path.join(self.pathtotimestamp_2, "*.dat*")
        )

        try:
            last_file_1 = max(DATA_FILES_1, key=os.path.getctime)
            last_file_2 = max(DATA_FILES_2, key=os.path.getctime)
            new_ctime_1 = os.path.getctime(last_file_1)
            new_ctime_2 = os.path.getctime(last_file_2)
        except ValueError:
            msg = QtWidgets.QMessageBox()
            msg.setText(
                "No data files found — check both working directories."
            )
            msg.setWindowTitle("Error")
            msg.exec_()
            self.slot_stopstream()
            stopping = True

        if not stopping:
            try:
                if (
                    new_ctime_1 > self.last_file_ctime_1
                    or new_ctime_2 > self.last_file_ctime_2
                ):
                    self.last_file_ctime_1 = new_ctime_1
                    self.last_file_ctime_2 = new_ctime_2

                    # Full-sensor data are always collected with the
                    # absolute timestamps, needed to synchronize the two
                    # boards, so no UI control is exposed for this.
                    rates_1 = sen_pop(
                        last_file_1,
                        board_number=self.comboBox_mask_2.currentText(),
                        fw_ver=self.comboBox_FW_2.currentText(),
                        timestamps=self.spinBox_timestamps_2.value(),
                        pix_add_fix=False,
                        absolute_timestamps=True,
                    )
                    # Pixel-address correction is always applied to board 2.
                    rates_2 = sen_pop(
                        last_file_2,
                        board_number=self.comboBox_mask_2.currentText(),
                        fw_ver=self.comboBox_FW_2.currentText(),
                        timestamps=self.spinBox_timestamps_2.value(),
                        pix_add_fix=True,
                        absolute_timestamps=True,
                    )

                    rates_1 = rates_1 * self.maskValidPixels
                    rates_2 = rates_2 * self.maskValidPixels_b2
                    combined = np.concatenate([rates_1, rates_2])

                    self.widget_figure.setPlotData(
                        np.arange(0, 512, 1),
                        combined,
                        [self.leftPosition, self.rightPosition],
                        self.grouping,
                        self.canvas_fontsize,
                    )

            except (ValueError, FileNotFoundError, OSError) as err:
                msg = QtWidgets.QMessageBox()
                msg.setText(
                    "Cannot read data file — it may have been removed. "
                    "Check the timestamp setting and the firmware "
                    "version; full-sensor data must hold the absolute "
                    "timestamps."
                )
                msg.setDetailedText(str(err))
                msg.setWindowTitle("Error")
                msg.exec_()
                self.slot_stopstream()

    # ------------------------------------------------------------------
    # Pixel masking
    # ------------------------------------------------------------------

    def mask_pixels(self):
        for i in range(256):
            self.maskValidPixels[i] = (
                0 if self.checkBoxPixel[i].isChecked() else 1
            )
            self.maskValidPixels_b2[i] = (
                0 if self.checkBoxPixel_b2[i].isChecked() else 1
            )

    def presetmask_pixels(self):
        """Load and apply preset masks for both boards.

        Each board uses the shared daughterboard and its own motherboard
        number to look up the mask file. Boards that have no mask file
        are silently skipped; an error is shown only if neither board has
        a mask.

        """
        if self.checkBox_presetMask_2.isChecked():
            any_loaded = False
            db = self.comboBox_mask_2.currentText()

            # Board 1
            try:
                f1 = files("daplis_rtp.params.masks").joinpath(
                    f"mask_{db}_{self.comboBox_mb_1.currentText()}.txt"
                )
                mask1 = np.genfromtxt(f1, delimiter=",", dtype="int")
                for i in mask1:
                    self.maskValidPixels[i] = 0
                    self.scrollAreaWidgetContentslayout.itemAt(
                        i
                    ).widget().setChecked(True)
                any_loaded = True
            except (IndexError, FileNotFoundError):
                pass

            # Board 2
            try:
                f2 = files("daplis_rtp.params.masks").joinpath(
                    f"mask_{db}_{self.comboBox_mb_2.currentText()}.txt"
                )
                mask2 = np.genfromtxt(f2, delimiter=",", dtype="int")
                for i in mask2:
                    self.maskValidPixels_b2[i] = 0
                    self.scrollAreaWidgetContentslayout_b2.itemAt(
                        i
                    ).widget().setChecked(True)
                any_loaded = True
            except (IndexError, FileNotFoundError):
                pass

            if not any_loaded:
                self.checkBox_presetMask_2.setCheckState(0)
                msg = QtWidgets.QMessageBox()
                msg.setText(
                    "No mask data found for the given daughterboard and "
                    "motherboard combination for either board."
                )
                msg.setWindowTitle("Error")
                msg.exec_()
        else:
            for i in range(256):
                self.scrollAreaWidgetContentslayout.itemAt(
                    i
                ).widget().setChecked(False)
                self.scrollAreaWidgetContentslayout_b2.itemAt(
                    i
                ).widget().setChecked(False)

    def reset_pix_mask(self):
        for i in range(256):
            self.scrollAreaWidgetContentslayout.itemAt(i).widget().setChecked(
                False
            )
            self.scrollAreaWidgetContentslayout_b2.itemAt(
                i
            ).widget().setChecked(False)
        self.checkBox_presetMask_2.setChecked(False)
