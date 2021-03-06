import xml.etree.ElementTree as ElementTree
import datetime
import numpy as np


# Read the XML file
def read_xml_file(xml_path, reperes_anato):
     #注意程序员
     #Kinovea中XML文件给出的结构是5级
     #结构上的第一次迭代（3是实际的Woorksheet）
     #行第3次迭代
     #列上的第4次迭代
    ws = 3  # worksheet
    tree = ElementTree.parse(xml_path)
    root = tree.getroot()[ws][0]  # We don't mind the first 2 columns of root 忽略前两列
    data = {}
    data_to_stack = np.ndarray((3, 1))  # Declare data stacker that keeps being updated (Time, X, Y)声明不断更新的数据堆栈器（时间，X，Y）
    for repere in reperes_anato:
        repere_found = False
        data_tp = np.ndarray((3, 0))  # Append all data
        # Find the data for each reperes
        for i in range(len(root)):
            # If we haven't reach the repere so far
            if not repere_found:
                if root[i][0][0].text is not None and len(root[i]) > 1 and root[i][1][0].text == repere:
                    repere_found = True
            # If we finished the repere
            elif len(root) <= i+3 or root[i+3][0][0].text is None:
                break
            # Otherwise add data
            else:
                data_to_stack[0, 0] = datetime.datetime.timestamp(datetime.datetime.strptime(root[i+3][2][0].text, "%H:%M:%S:%f")                )
                data_to_stack[1, 0] = root[i+3][0][0].text
                data_to_stack[2, 0] = root[i+3][1][0].text
                data_tp = np.hstack((data_tp, data_to_stack))

        # If we get here and haven't found the repere, raise an error
        if not repere_found:
            raise LookupError(repere + " was not found in the document")
        data[repere] = data_tp  # Save the data

    # Find share timestamps
    # Arbitrarily take the time of first repere as time reference
    shared_time = data[reperes_anato[0]][0, :]
    shared_time = np.unique(shared_time)
    for d in data.values():
        shared_time_tp = d[0, np.isin(d[0, :], shared_time)]
        shared_time = shared_time[np.isin(shared_time, shared_time_tp)]

    # Remove unshared timestamps
    for (k, d) in data.items():
        idx = np.isin(d[0, :], shared_time)
        _, idx = np.unique(d[0, idx], return_index=True)
        data[k] = d[1:3, idx] * 0.01  # From cm to m

    # Return data
    time = shared_time - shared_time[0]
    return data, time


def convert_to3d(data):
    n_frame = data[list(data.keys())[0]].shape[1]
    new_data = np.ndarray((2, len(data), n_frame))
    for i, m in enumerate(data.values()):
        new_data[:, i, :] = m
    return new_data


def dispatch_dict(data):
    new_data = np.ndarray((data[list(data.keys())[0]].shape[0], len(data), data[list(data.keys())[0]].shape[2]))
    for i, m in enumerate(data.values()):
        new_data[:, i, :] = m[:, 0, :]
    return new_data


def to_degree(data):
    return data * 180/np.pi
