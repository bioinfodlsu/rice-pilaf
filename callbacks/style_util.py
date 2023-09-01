def add_class_name(class_name, current_class_name):
    current_classes = current_class_name.split(' ')
    current_classes.append(class_name)

    return ' '.join(current_classes)


def remove_class_name(class_name, current_class_name):
    current_classes = current_class_name.split(' ')

    return ' '.join([current_class for current_class in current_classes if current_class != class_name])
