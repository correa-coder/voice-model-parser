import unittest

from package.parsers.voice_model import VoiceModel, VoiceModelParser
from package.utils.helpers import NumberConverter, InfoExtractor


class InfoExtractorTests(unittest.TestCase):
    
    def test_extract_epochs(self):
        self.assertEqual(InfoExtractor.extract_epochs('ModelName (RVC v2) 44k steps'), -1)
        self.assertEqual(InfoExtractor.extract_epochs('ModelName (RVC v2)'), -1)
        self.assertEqual(InfoExtractor.extract_epochs('ModelName (RVC v2) 800 epoch'), 800)
        self.assertEqual(InfoExtractor.extract_epochs('ModelName (RVC v2) 800 epochs'), 800)
        self.assertEqual(InfoExtractor.extract_epochs('ModelName (RVC v2) 1k Epoch'), 1000)
        self.assertEqual(InfoExtractor.extract_epochs('ModelName (RVC v2) 1.2k Epochs'), 1200)
        self.assertEqual(InfoExtractor.extract_epochs('ModelName (RVC v2) 1.05k Epoch'), 1050)
        self.assertEqual(InfoExtractor.extract_epochs('ModelName (RVC v2) 2k EPOCH'), 2000)
        self.assertEqual(InfoExtractor.extract_epochs('ModelName (250 EPOCHS)'), 250)

    def test_extract_steps(self):
        self.assertEqual(InfoExtractor.extract_steps('ModelName (RVC v2) 800 epochs'), -1)
        self.assertEqual(InfoExtractor.extract_steps('ModelName (RVC v2) 100 step'), 100)
        self.assertEqual(InfoExtractor.extract_steps('ModelName (RVC v2) 44k steps'), 44000)
        self.assertEqual(InfoExtractor.extract_steps('ModelName (RVC v2) 44k STEP'), 44000)
        self.assertEqual(InfoExtractor.extract_steps('ModelName (RVC v2) (44.12k STEPS)'), 44120)

    def test_extract_name(self):
        self.assertEqual(InfoExtractor.extract_name('Jhay Cortez (RVC) 250 Epoch'), 'Jhay Cortez')
        self.assertEqual(InfoExtractor.extract_name('Gummibär (RVC v2) 300 Epoch'), 'Gummibär')
        self.assertEqual(InfoExtractor.extract_name('Jeno (From NCT) (RVC) 350 Epoch 11k Steps'), 'Jeno (From NCT)')
        self.assertEqual(InfoExtractor.extract_name('Maeve (From Paladins) RVC 1.6k Epoch'), 'Maeve (From Paladins)')
        self.assertEqual(InfoExtractor.extract_name('Britney Spears 100k', is_rvc=False), 'Britney Spears')
        self.assertEqual(InfoExtractor.extract_name('Britney Spears', is_rvc=False), 'Britney Spears')

    def test_extract_links(self):
        sample1 = 'Here is the link https://drive.google.com/file/d/1Rn7dOfD3BvZjUP36pAEv8VCYJC9clogS/view?usp=sharing'
        sample1_links = ['https://drive.google.com/file/d/1Rn7dOfD3BvZjUP36pAEv8VCYJC9clogS/view?usp=sharing']
        self.assertEqual(InfoExtractor.extract_links(sample1), sample1_links)

        sample2 = 'Model: https://drive.google.com/file/d/1Rn7dOfD3BvZjUP36pAEv8VCYJC9clogS/view?usp=sharing\nDataset: https://drive.google.com/file/d/1Rn7dOfD3BvZjUP36pAEv8VCYJC9clogS/view?usp=sharing'
        sample2_links = [
            'https://drive.google.com/file/d/1Rn7dOfD3BvZjUP36pAEv8VCYJC9clogS/view?usp=sharing',
            'https://drive.google.com/file/d/1Rn7dOfD3BvZjUP36pAEv8VCYJC9clogS/view?usp=sharing'
        ]
        self.assertEqual(InfoExtractor.extract_links(sample2), sample2_links)

        sample3 = 'Link 1 (MEGA): https://mega.nz/file/1fUjzTYQ#wrCJhg-r0LpRdYQJfuqao_f7JN6phJFQjrTpNlY_aVo'
        sample3_links = [
            'https://mega.nz/file/1fUjzTYQ#wrCJhg-r0LpRdYQJfuqao_f7JN6phJFQjrTpNlY_aVo'
        ]
        self.assertEqual(InfoExtractor.extract_links(sample3), sample3_links)


class TestNumberConverter(unittest.TestCase):
    
    def test_to_str(self):
        self.assertEqual(NumberConverter.to_string(1000), '1k')
        self.assertEqual(NumberConverter.to_string(4000), '4k')
        self.assertEqual(NumberConverter.to_string(44100), '44.1k')
        self.assertEqual(NumberConverter.to_string(600), '600')

    def test_from_str(self):
        self.assertEqual(NumberConverter.from_string('44.1k'), 44100)
        self.assertEqual(NumberConverter.from_string('44.1K'), 44100)
        self.assertEqual(NumberConverter.from_string('1k'), 1000)
        self.assertEqual(NumberConverter.from_string('600'), 600)


class TestVoiceModel(unittest.TestCase):

    def setUp(self):
        self.voice1 = VoiceModel(
            title='Jihyo (From TWICE)',
            author='user1',
            tags=['Singer', 'Korean', 'RVC'],
            epochs=1000)

        self.voice2 = VoiceModel(
            title='BLACKPINK JENNIE',
            author='user2', 
            tags=['Singer', 'Korean', 'RVC V2'],
            epochs=400, steps=44100)
        
        self.voice3 = VoiceModel(
            title='Rosé',
            author='user3',
            tags=['Singer', 'Korean', 'RVC V2'],
            epochs=1200, steps=44100)

    def tearDown(self):
        del self.voice1
        del self.voice2
        del self.voice3

    def test_voice_group(self):
        self.assertTrue(self.voice1.has_group)
        self.assertTrue(self.voice2.has_group)
        self.assertFalse(self.voice3.has_group)

        self.assertEqual(self.voice1.group, 'TWICE')
        self.assertEqual(self.voice2.group, 'BLACKPINK')
        self.assertEqual(self.voice3.group, 'No Group')

    def test_voice_name(self):
        self.assertEqual(self.voice1.name, 'Jihyo')
        self.assertEqual(self.voice2.name, 'Jennie')
        self.assertEqual(self.voice3.name, 'Rosé')

    # string representation
    def test_voice_to_str(self):
        self.assertEqual(str(self.voice1), 'Jihyo (From TWICE) (RVC) 1k Epochs')
        self.assertEqual(str(self.voice2), 'Jennie (From BLACKPINK) (RVC v2) 400 Epochs 44.1k Steps')
        self.assertEqual(str(self.voice3), 'Rosé (RVC v2) 1.2k Epochs 44.1k Steps')

if __name__ == '__main__':
    unittest.main()
