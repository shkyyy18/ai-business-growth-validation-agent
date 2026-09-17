"""Synthetic transport fixtures; never counted as real content evidence."""
import importlib.util
import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location('professional_inspector',ROOT/'research/m1-professional-2026-09-14/inspect_cached_pages.py')
mod=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)

def html(*parts):
    return ''.join('<script>self.__pace_f.push('+json.dumps([1,p],ensure_ascii=False)+')</script>' for p in parts)

class FrameTests(unittest.TestCase):
    def test_json_chunk_boundary(self):
        frames,texts=mod.decode_frames(html('7:{"x":', '"中"}\n'))
        self.assertEqual(frames,[('frame:7',{'x':'中'})])
        self.assertEqual(texts,{})
    def test_text_length_is_bytes_and_embedded_headers_are_inert(self):
        value='中文\n9:{"fake":true}\n末尾'
        payload='a:T'+format(len(value.encode('utf-8')),'x')+','+value+'b:{"asr":"$a"}\n'
        frames,texts=mod.decode_frames(html(payload[:15],payload[15:]))
        self.assertEqual(frames,[('frame:b',{'asr':'$a'})])
        self.assertEqual(mod.resolve_asr('$a',texts),(value,'frame:a'))
    def test_unresolved_and_special_refs(self):
        for value in ['$undefined','$null','$a','$L7',None,'']:
            self.assertEqual(mod.resolve_asr(value,{}),(None,None))
    def test_direct_text(self):
        self.assertEqual(mod.resolve_asr('正文',{}),('正文',None))
    def test_truncated_text_rejected(self):
        with self.assertRaises(ValueError):mod.decode_frames(html('a:Tff,short'))
    def test_invalid_utf8_length_rejected(self):
        with self.assertRaises(UnicodeDecodeError):mod.decode_frames(html('a:T1,中'))
    def test_duplicate_id_rejected(self):
        with self.assertRaises(ValueError):mod.decode_frames(html('7:{}\n7:{}\n'))
    def test_unknown_frame_type_skipped(self):
        frames,_=mod.decode_frames(html('1:I["module"]\n7:{}\n'))
        self.assertEqual(frames,[('frame:7',{})])
    def test_ordinary_javascript_not_executed(self):
        frames,texts=mod.decode_frames('<script>throw new Error("never run")</script>')
        self.assertEqual((frames,texts),([],{}))

if __name__=='__main__':unittest.main()
