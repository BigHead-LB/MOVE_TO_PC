import sys
import os
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, QThread, QTimer
from Tektronix_DPO_4104_function import ScopeWorker


class InstrumentApp:
    def __init__(self):
        loader = QUiLoader()
        # 自动获取当前目录下的 UI 文件
        ui_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Tektronix_DPO_4104_waveformk.ui")
        ui_file = QFile(ui_path)
        if not ui_file.open(QFile.ReadOnly):
            print("找不到 UI 文件")
            return
        self.ui = loader.load(ui_file)
        ui_file.close()

        if self.ui:
            # --- 默认参数设置 ---
            if hasattr(self.ui, 'input_address'):
                self.ui.input_address.setText("USB0::0x0699::0x0401::C022270::INSTR")
            self.ui.sb_catch.clicked.connect(self.run_process)
            self.ui.setWindowTitle("Tektronix DPO 4104 自动化采集系统")

    def run_process(self):
        addr = self.ui.input_address.text()
        ch = self.ui.sb_channel.value()
        if not addr:
            QMessageBox.warning(self.ui, "错误", "请输入有效的 VISA 地址")
            return

        # 1. 启动线程逻辑
        self.thread = QThread()
        self.worker = ScopeWorker(addr, ch)
        self.worker.moveToThread(self.thread)

        # 2. 信号绑定 (注意：这里调用的方法必须在下面定义)
        self.thread.started.connect(self.worker.run_capture_task)
        self.worker.status_update.connect(lambda m: self.ui.label_status.setText(m))
        self.worker.finished.connect(self.handle_success)  # 之前报错就在这里
        self.worker.error.connect(self.handle_error)  # 异常处理

        # 3. 退出清理逻辑
        self.worker.finished.connect(self.thread.quit)
        self.worker.error.connect(self.thread.quit)
        self.thread.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.ui.sb_catch.setEnabled(False)
        self.thread.start()

    # --- 这里是刚才缺失的 handle_success 方法 ---
    def handle_success(self, variation):
        if hasattr(self.ui, 'label_result'):
            self.ui.label_result.setText(f"波动率: {variation:.4%}")

        self.ui.sb_catch.setEnabled(True)
        self.ui.label_status.setText("采集成功")

        # 异步弹窗，防止死锁
        QTimer.singleShot(200, lambda: QMessageBox.information(
            self.ui, "处理完成", f"原始文件与滤波文件已保存！\n最终波动率: {variation:.4%}"
        ))

    # --- 这里是刚才缺失的 handle_error 方法 ---
    def handle_error(self, err_msg):
        self.ui.sb_catch.setEnabled(True)
        self.ui.label_status.setText("执行异常")
        QMessageBox.critical(self.ui, "运行错误", f"程序未能完成采集。\n原因: {err_msg}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_app = InstrumentApp()
    if main_app.ui:
        main_app.ui.show()
        sys.exit(app.exec())