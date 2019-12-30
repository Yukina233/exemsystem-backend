import json

class StuExamHelper:
    def __init__(self):
        pass

    def __del__(self):
        pass

    def CreateAvaList(self):
        obj = {
            'count':0,
            'ava_list':[]
        }
        return obj

    def AddAvaPaper(self,ava_list,paper_id):
        paper_obj = {'paper': paper_id}
        ava_list['ava_list'].append(paper_obj)
        ava_list['count'] += 1

    def DelAvaPaper(self,ava_list,paper_id):
        papers = ava_list['ava_list']
        paper_obj = {'paper': paper_id}
        try:
            i = papers.index(paper_obj)
            papers.pop(i)
            ava_list['count'] -= 1
        except:
            print('error from StuExamHelper DelAvaPaper : paper id ' + str(paper_id) + ' does not exist')

    def ExistAvaPaper(self, ava_list, paper_id):
        papers = ava_list['ava_list']
        paper_obj = {'paper': paper_id}
        if (paper_obj in papers):
            return True
        else:
            return False