import os
from unittest.mock import MagicMock, patch

from . import PluginTestCase


class Given_TCMS_BUILD_IsPresent(PluginTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.plugin._rpc = MagicMock()
        cls.plugin._rpc.Build.filter = MagicMock(
            return_value=[{'build_id': 40}])

    def test_when_get_build_id_then_will_use_it(self):
        with patch.dict(os.environ, {
                'TCMS_BUILD': 'b.Test',
                'TRAVIS_BUILD_NUMBER': 'travis-25',
                'BUILD_NUMBER': '48',
        }):
            build_id, build_number = self.plugin.get_build_id(0, 0)
            self.assertEqual(build_id, 40)
            self.assertEqual(build_number, 'b.Test')


class Given_TRAVIS_BUILD_NUMBER_IsPresent(PluginTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.plugin._rpc = MagicMock()
        cls.plugin._rpc.Build.filter = MagicMock(
            return_value=[{'build_id': 40}])

    def test_when_get_build_id_then_will_use_it(self):
        with patch.dict(os.environ, {
                'TRAVIS_BUILD_NUMBER': 'travis-25',
                'BUILD_NUMBER': 'jenkins-48',
        }):
            build_id, build_number = self.plugin.get_build_id(0, 0)
            self.assertEqual(build_id, 40)
            self.assertEqual(build_number, 'travis-25')


class Given_BUILD_NUMBER_IsPresent(PluginTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.plugin._rpc = MagicMock()
        cls.plugin._rpc.Build.filter = MagicMock(
            return_value=[{'build_id': 40}])

    def test_when_get_build_id_then_will_use_it(self):
        with patch.dict(os.environ, {
                'BUILD_NUMBER': 'jenkins-48',
        }):
            build_id, build_number = self.plugin.get_build_id(0, 0)
            self.assertEqual(build_id, 40)
            self.assertEqual(build_number, 'jenkins-48')


class GivenBuildEnvironmentIsNotPresent(PluginTestCase):
    def test_when_get_build_id_then_will_raise(self):
        with patch.dict(os.environ, {}):
            with self.assertRaisesRegex(Exception,
                                        'Build number not defined'):
                self.plugin.get_build_id(0, 0)


class GivenBuildExistsInDatabase(PluginTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.plugin._rpc = MagicMock()
        cls.plugin._rpc.Build.filter = MagicMock(
            return_value=[{'build_id': 40}])
        cls.plugin._rpc.Build.create = MagicMock(
            return_value={'build_id': 50})

    def test_when_get_build_id_then_will_reuse_it(self):
        with patch.dict(os.environ, {
                'TCMS_BUILD': 'b.Test',
        }):
            build_id, build_number = self.plugin.get_build_id(0, 0)
            self.assertEqual(build_id, 40)
            self.assertEqual(build_number, 'b.Test')
            self.plugin._rpc.Build.create.assert_not_called()


class GivenBuildDoesntExistInDatabase(PluginTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.plugin._rpc = MagicMock()
        cls.plugin._rpc.Build.filter = MagicMock(return_value=[])
        cls.plugin._rpc.Build.create = MagicMock(
            return_value={'build_id': 50})

    def test_when_get_build_id_then_will_add_it(self):
        with patch.dict(os.environ, {
                'TCMS_BUILD': 'b.Test',
        }):
            build_id, build_number = self.plugin.get_build_id(0, 0)
            self.assertEqual(build_id, 50)
            self.assertEqual(build_number, 'b.Test')
            self.plugin._rpc.Build.create.assert_called_with({
                'name': 'b.Test',
                'product': 0})
