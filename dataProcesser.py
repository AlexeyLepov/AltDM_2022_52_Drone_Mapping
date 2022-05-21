import cv2
import numpy as np


def importData(fileName, imageDirectory):
    '''
    ===============================================================================================
    Функция чтения исходных данных, поступающих с дрона.
    Исходные данные представляют собой фотоснимки и файл с информацией о положении дрона в момент
    выполнения снимка.
    ===============================================================================================
    Принимает : fileName - имя файла данных в строковой форме, например. "data/telemetry.txt"
    Принимает : imageDirectory - имя каталога, в котором хранятся изображения. "data/"
    ===============================================================================================
    Возвращает: dataMatrix (Тип: NumPy ndArray) - массив, содержащий все данные позиции, где в 
        каждой строке хранится 6 плавающих элементов, содержащих информацию в форме [XYZYPR].
    Возвращает: allImages (Тип: NumPy ndArray) - список, содержащий изображения.
    ===============================================================================================
    '''
    allImages = [] # Массив изображений
    fileNameMatrix = np.genfromtxt(fileName,delimiter=",",usecols=[0],dtype=str) # чтение имени файла-изображения
    dataMatrix = np.genfromtxt(fileName,delimiter=",",usecols=range(1,7),dtype=float) # чтение числовых данных

    # чтение изображений по имени файла из текстового документа
    for i in range(0,fileNameMatrix.shape[0]): 
        allImages.append(cv2.imread(imageDirectory+fileNameMatrix[i]))
    
    # перевод характеристик дрона Lat и Lon в координаты x,y,z
    for i in range(0,fileNameMatrix.shape[0]): 
        lat = dataMatrix[[i],[0]]
        lon = dataMatrix[[i],[1]]
        temp = dataMatrix[[i],[3]]

        # Вычисление координат
        lat, lon = np.deg2rad(lat), np.deg2rad(lon) # перевод градусных мер в радианную
        EarthRad = 6371 # приблизительный радиус Земли в километрах
        x = EarthRad * np.cos(lat) * np.cos(lon) # Вычисление координаты x
        y = EarthRad * np.cos(lat) * np.sin(lon) # Вычисление координаты y
        z = EarthRad * np.sin(lat) # Вычисление координаты z

        # Присвоение списку ndarray вычисленных значений и приведение их к виду [XYZYPR]
        dataMatrix[[i],[0]] = x
        dataMatrix[[i],[1]] = y
        dataMatrix[[i],[2]] = z
        dataMatrix[[i],[3]] = dataMatrix[[i],[5]]
        dataMatrix[[i],[5]] = temp
    
    return allImages, dataMatrix


def display(title, image):
    '''
    ===============================================================================================
    Механизм OpenCV для показа изображения.
    ===============================================================================================
    Принимает : title - заголовок окна в строковой форме.
    Принимает : image (Тип: ndArray) - переменная, содержащая изображение для показа
    ===============================================================================================
    Выполняет вывод на экран изображений в течении 0.8 секунд. 
    ===============================================================================================
    '''
    cv2.namedWindow(title,cv2.WINDOW_NORMAL)
    cv2.resizeWindow(title,1600,900)
    cv2.moveWindow(title,0,0)
    cv2.imshow(title,image)
    cv2.waitKey(800)
    cv2.destroyWindow(title)


def drawMatches(img1, kp1, img2, kp2, matches):
    """
    ===============================================================================================
    Монтаж изображений.
    ===============================================================================================
    Принимает : img1 - первый фотоснимок в черно-белом
    Принимает : kp1 - точки сопоставления у первого фотоснимка
    Принимает : img2 - второй фотоснимок в черно-белом
    Принимает : kp2 - точки сопоставления у второго фотоснимка
    Принимает : matches - массив совпадений
    ===============================================================================================
    Возвращает: out - два изображения с 
    ===============================================================================================
    """
    # Создание нового выходного изображения, которое объединяет два изображения вместе.
    rows1 = img1.shape[0]
    cols1 = img1.shape[1]
    rows2 = img2.shape[0]
    cols2 = img2.shape[1]
    out = np.zeros((max([rows1,rows2]),cols1+cols2,3), dtype='uint8')
    # Вставка первого изображения слева
    out[:rows1,:cols1] = np.dstack([img1])
    # Вставка следующего изображения справа от него
    out[:rows2,cols1:] = np.dstack([img2])

    # Для каждой пары точек между обоими изображениями рисуются круги, а затем соединяются линиями
    for m in matches:
        # Получение соответствующих ключевых точек для каждого из изображений
        img1_idx = m.queryIdx
        img2_idx = m.trainIdx

        # x - столбцы
        # y - ряды
        (x1,y1) = kp1[img1_idx].pt
        (x2,y2) = kp2[img2_idx].pt

        # Рисование круга по обеим координатам
        radius = 8
        thickness = 4
        color_lines = (40,200,180) # цвет линий
        color_circle = (210,40,80) # цвет кругов
        cv2.circle(out, (int(x1),int(y1)), radius, color_circle, thickness)
        cv2.circle(out, (int(x2)+cols1,int(y2)), radius, color_circle, thickness)
        # Рисование линии между двумя точками
        cv2.line(out, (int(x1),int(y1)), (int(x2)+cols1,int(y2)), color_lines, 2)

    # Возврат изображения
    return out