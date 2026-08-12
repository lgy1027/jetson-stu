# 单个二维检测结果。坐标采用左上角和右下角的 xyxy 格式。
std_msgs/Header header
string label
float32 score
int32 x_min
int32 y_min
int32 x_max
int32 y_max
