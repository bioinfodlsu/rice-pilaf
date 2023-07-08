def add_class_name(class_name, current_class_name):
    current_classes = current_class_name.split(' ')
    current_classes.append(class_name)

    return ' '.join(current_classes)


def remove_class_name(class_name, current_class_name):
    current_classes = current_class_name.split(' ')
    try:
        current_classes.remove(class_name)
    except ValueError:
        pass

    return ' '.join(current_classes)
