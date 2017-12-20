import unittest
import random

import numpy as np
import cv2

from data_processing import CamVid, crop_images, encoding_mask, decoding_mask
from data_processing import preprocess_data


class TestCamVid(unittest.TestCase):
    def setUp(self):
        self._data = CamVid()

        self.images_test = []
        self.labels_test = []
        for i in range(5):
            self.images_test.append(
                cv2.imread(random.choice(self._data.image_files_train)))
            self.labels_test.append(
                cv2.imread(random.choice(self._data.label_files_train)))
            self.images_test.append(
                cv2.imread(random.choice(self._data.image_files_vali)))
            self.labels_test.append(
                cv2.imread(random.choice(self._data.label_files_vali)))

        self.label_names = self._data.label_names
        self.label_colors = self._data.label_colors
        self.n_classes = self._data.n_classes

    def test_class_names(self):
        self.assertEqual(self.n_classes, 12)
        self.assertEqual(len(self.label_names), 12)
        self.assertEqual(len(self.label_colors), 12)
        self.assertEqual(self.label_names[0], 'Bicyclist')
        self.assertEqual(self.label_colors[0], (0, 128, 192))
        self.assertEqual(self.label_names[-1], 'Void')
        self.assertEqual(self.label_colors[-1], (0, 0, 0))

    def test_split_data(self):
        self.assertEqual(len(self._data.image_files_vali), 112)
        self.assertEqual(len(self._data.label_files_vali), 112)
        self.assertEqual(len(self._data.image_files_train), 448)
        self.assertEqual(len(self._data.label_files_train), 448)
        self.assertEqual(len(self._data.image_files_test), 141)
        self.assertEqual(len(self._data.label_files_test), 141)

    def test_image_size(self):
        for img, label in zip(self.images_test, self.labels_test):
            self.assertEqual(img.shape, (720, 960, 3))
            self.assertEqual(label.shape, (720, 960, 3))

    def test_crop_image(self):
        target_shape = (320, 480)
        for img_, gt_img_ in zip(self.images_test, self.labels_test):
            img, gt_img = crop_images(img_, gt_img_, target_shape, is_training=False)
            self.assertEqual(img.shape, (*target_shape, 3))
            self.assertEqual(gt_img.shape, (*target_shape, 3))
            # Unique colors are invariant during cropping
            self.assertLessEqual(set(tuple(v) for m2d in gt_img for v in m2d),
                                 set(tuple(v) for m2d in gt_img_ for v in m2d))

    def test_encoding_decoding_mask(self):
        for label in self.labels_test:
            mask_encoded = encoding_mask(label, self.label_colors, is_rgb=False)
            self.assertEqual(mask_encoded.shape[2], len(self.label_names))
            self.assertEqual(sorted(np.unique(mask_encoded)), [0, 1])

            mask_decoded = decoding_mask(np.argmax(mask_encoded, axis=2),
                                         self.label_colors,
                                         is_rgb=False)
            self.assertLessEqual(
                len(set(tuple(v) for m2d in mask_decoded for v in m2d)),
                self.n_classes)

    def test_data_processing(self):
        target_shape = (320, 480)
        images, labels = preprocess_data(self.images_test,
                                         self.labels_test,
                                         self.label_colors,
                                         input_shape=target_shape)
        self.assertEqual(images.shape[0], len(self.images_test))
        self.assertEqual(labels.shape[0], len(self.labels_test))
        for X, Y in zip(images, labels):
            self.assertLessEqual(-1, X.min())
            self.assertGreaterEqual(1, X.max())
            self.assertEqual(X.shape, (*target_shape, 3))
            self.assertEqual(Y.shape,
                             (target_shape[0], target_shape[1], self.n_classes))
            self.assertEqual(sorted(np.unique(Y)), [0, 1])


if __name__ == "__main__":
    unittest.main()
