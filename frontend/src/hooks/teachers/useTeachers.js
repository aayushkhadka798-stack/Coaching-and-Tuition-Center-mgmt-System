import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import * as teacherApi from '../../api/teacherApi'

export const teacherKeys = { all: ['teachers'] }
export function useTeacherList(params) {
  return useQuery({ queryKey: [...teacherKeys.all, params], queryFn: () => teacherApi.listTeachers(params).then(({ data }) => data) })
}
function mutation(method) {
  return () => {
    const client = useQueryClient()
    return useMutation({ mutationFn: method, onSuccess: () => client.invalidateQueries({ queryKey: teacherKeys.all }) })
  }
}
export const useCreateTeacher = mutation(teacherApi.createTeacher)
export const useUpdateTeacher = mutation(({ id, payload }) => teacherApi.updateTeacher(id, payload))
export const useDeleteTeacher = mutation(teacherApi.deleteTeacher)
